"""Retrieval de similaridade harmônica por música (Camada C).

Constrói um embedding harmônico por música a partir do corpus persistido — reusando
o `Fingerprint` de `domain/style_fingerprint` (grão de artista → aqui, grão de
música) — e materializa os top-K vizinhos por cosseno. Transposição-invariante
(features de FUNÇÃO, não de tom), interpretável, sem ML pesado.

Descritivo: só LÊ o banco; NUNCA reescreve `function_code`, arbitra centro, ou toca
gates. Similaridade é relação entre músicas, NÃO veredito de qualidade.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harmonic_analysis.domain.style_fingerprint import Fingerprint, similarity

if TYPE_CHECKING:
    import duckdb

_NEIGHBOR_DDL = """
CREATE TABLE IF NOT EXISTS song_neighbor (
    run_id       INTEGER,
    song_id      INTEGER,
    neighbor_id  INTEGER,
    rank         INTEGER,
    similarity   DOUBLE,
    PRIMARY KEY (run_id, song_id, neighbor_id)
);
"""

_NEIGHBOR_VIEW = """
CREATE OR REPLACE VIEW v_song_neighbor AS
SELECT
    n.song_id,
    s.title           AS song_title,
    s.slug            AS song_slug,
    n.rank,
    n.neighbor_id,
    nb.title          AS neighbor_title,
    nb.slug           AS neighbor_slug,
    nb.completeness   AS neighbor_completeness,
    n.similarity
FROM song_neighbor n
JOIN v_song_current s  ON n.song_id = s.song_id AND n.run_id = s.run_id
JOIN v_song_current nb ON n.neighbor_id = nb.song_id AND n.run_id = nb.run_id
ORDER BY n.song_id, n.rank;
"""


def _current_run_id(conn: "duckdb.DuckDBPyConnection") -> int:
    row = conn.execute("SELECT max(run_id) FROM analysis_run").fetchone()
    if row is None or row[0] is None:
        raise RuntimeError("Banco sem run — rode `harmonic corpus build` primeiro.")
    return int(row[0])


def fingerprint_from_db(
    conn: "duckdb.DuckDBPyConnection", song_id: int
) -> Fingerprint:
    """Monta o `Fingerprint` de uma música a partir dos agregados do banco.

    Mesma forma do `build_fingerprint` (grão de artista), mas `song_count = 1`. A
    densidade de tensão é a fração de funções não-repouso (`function_ref.is_repose`
    = FALSE) — o análogo derivável do banco, transposição-invariante.
    """
    funcs = [
        r[0]
        for r in conn.execute(
            "SELECT function_code FROM chord_occurrence "
            "WHERE song_id = ? AND function_code IS NOT NULL ORDER BY position",
            [song_id],
        ).fetchall()
    ]
    # Distribuição de função (soma 1).
    total = len(funcs)
    dist: dict[str, float] = {}
    if total:
        from collections import Counter

        for f, c in sorted(Counter(funcs).items()):
            dist[f] = c / total

    # Matriz de transição normalizada por linha.
    from collections import Counter, defaultdict

    trans_counter: dict[str, Counter] = defaultdict(Counter)
    for a, b in zip(funcs, funcs[1:]):
        trans_counter[a][b] += 1
    transition: dict[str, dict[str, float]] = {}
    for src, counter in trans_counter.items():
        row_total = sum(counter.values())
        transition[src] = {dst: counter[dst] / row_total for dst in sorted(counter)}

    # Contagem de cadências (só as não suprimidas contam como cadência real).
    cadence_counts = {
        r[0]: r[1]
        for r in conn.execute(
            "SELECT family, COUNT(*) FROM cadence "
            "WHERE song_id = ? AND NOT suppressed GROUP BY family",
            [song_id],
        ).fetchall()
    }

    # Uso modal: 1.0 se a música tem qualquer modal_coloring, senão 0.0.
    modal = conn.execute(
        "SELECT COUNT(*) FROM modal_coloring WHERE song_id = ?", [song_id]
    ).fetchone()[0]
    modal_usage = 1.0 if modal else 0.0

    # Densidade de tensão = fração de funções não-repouso.
    tension = conn.execute(
        "SELECT COUNT(*) FROM chord_occurrence o "
        "JOIN function_ref f ON o.function_code = f.function_code "
        "WHERE o.song_id = ? AND NOT f.is_repose",
        [song_id],
    ).fetchone()[0]
    tension_density = tension / total if total else 0.0

    return Fingerprint(
        function_distribution=dist,
        transition_matrix=transition,
        cadence_counts=cadence_counts,
        modal_usage=modal_usage,
        tension_density=tension_density,
        song_count=1,
    )


def build_neighbors(conn: "duckdb.DuckDBPyConnection", k: int = 10) -> dict:
    """Materializa os top-K vizinhos por cosseno para o run corrente.

    Idempotente: recomputa só o run corrente. Reusa `style_fingerprint.similarity`
    (cosseno sobre o vetor concatenado, transposição-invariante).
    """
    run_id = _current_run_id(conn)
    songs = [
        r[0]
        for r in conn.execute(
            "SELECT song_id FROM v_song_current ORDER BY song_id"
        ).fetchall()
    ]
    fps = {sid: fingerprint_from_db(conn, sid) for sid in songs}

    records: list[tuple] = []
    for sid in songs:
        sims = [
            (other, similarity(fps[sid], fps[other]))
            for other in songs
            if other != sid
        ]
        # Ordena por similaridade desc, desempate estável por song_id.
        sims.sort(key=lambda t: (-t[1], t[0]))
        for rank, (neighbor_id, sim) in enumerate(sims[:k], start=1):
            records.append((run_id, sid, neighbor_id, rank, sim))

    conn.execute(_NEIGHBOR_DDL)
    conn.execute("DELETE FROM song_neighbor WHERE run_id = ?", [run_id])
    conn.executemany(
        "INSERT INTO song_neighbor "
        "(run_id, song_id, neighbor_id, rank, similarity) VALUES (?, ?, ?, ?, ?)",
        records,
    )
    conn.execute(_NEIGHBOR_VIEW)
    return {"run_id": run_id, "n_songs": len(songs), "k": k, "n_edges": len(records)}


def shared_traits(fp_a: Fingerprint, fp_b: Fingerprint, top: int = 3) -> dict:
    """Traços harmônicos salientes em comum — o 'porquê' da proximidade.

    Funções em comum entre as top-`top` de cada distribuição, e famílias de
    cadência presentes nas duas. Descritivo, não veredito.
    """
    def _top_funcs(fp):
        return {
            f for f, _ in sorted(
                fp.function_distribution.items(), key=lambda t: -t[1]
            )[:top]
        }

    common_funcs = sorted(_top_funcs(fp_a) & _top_funcs(fp_b))
    common_cadences = sorted(set(fp_a.cadence_counts) & set(fp_b.cadence_counts))
    return {"functions": common_funcs, "cadences": common_cadences}


def resolve_slug(conn: "duckdb.DuckDBPyConnection", slug: str):
    """slug → song_id no run corrente; None se não existir."""
    row = conn.execute(
        "SELECT song_id FROM v_song_current WHERE slug = ?", [slug]
    ).fetchone()
    return row[0] if row else None


def neighbors_up_to_date(conn: "duckdb.DuckDBPyConnection") -> bool:
    """True se `song_neighbor` já cobre o run corrente."""
    try:
        run_id = _current_run_id(conn)
    except RuntimeError:
        return False
    exists = conn.execute(
        "SELECT COUNT(*) FROM information_schema.tables "
        "WHERE table_name = 'song_neighbor'"
    ).fetchone()[0]
    if not exists:
        return False
    n = conn.execute(
        "SELECT COUNT(*) FROM song_neighbor WHERE run_id = ?", [run_id]
    ).fetchone()[0]
    return n > 0
