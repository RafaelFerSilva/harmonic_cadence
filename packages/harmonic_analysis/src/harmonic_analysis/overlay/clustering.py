"""Agrupamento hierárquico das músicas por perfil harmônico (Camada C).

Descobre **famílias harmônicas** no corpus e a **música-protótipo (medoid)** de cada
uma, por agrupamento aglomerativo (*average-linkage*) sobre a distância de cosseno
entre os embeddings de `overlay/similarity`. Puro Python, sem dependência ML (293
músicas é trivial), reusando os vetores de `style_fingerprint` num eixo de funções
GLOBAL (comparabilidade). Transposição-invariante (features de FUNÇÃO).

Descritivo: só LÊ o banco; NUNCA reescreve `function_code`, arbitra centro, ou toca
gates. Família é relação descritiva, NÃO veredito de qualidade. O `k` é do usuário —
sem alegação de "k ótimo".
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harmonic_analysis.domain.style_fingerprint import _cosine, _feature_vector
from harmonic_analysis.overlay.similarity import fingerprint_from_db

if TYPE_CHECKING:
    import duckdb

_CLUSTER_DDL = """
CREATE TABLE IF NOT EXISTS song_cluster (
    run_id      INTEGER,
    song_id     INTEGER,
    cluster_id  INTEGER,
    is_medoid   BOOLEAN,
    PRIMARY KEY (run_id, song_id)
);
"""

_CLUSTER_VIEW = """
CREATE OR REPLACE VIEW v_song_cluster AS
SELECT
    c.cluster_id,
    c.song_id,
    s.title        AS song_title,
    s.slug         AS song_slug,
    s.completeness,
    c.is_medoid
FROM song_cluster c
JOIN v_song_current s ON c.song_id = s.song_id AND c.run_id = s.run_id
ORDER BY c.cluster_id, c.is_medoid DESC, s.title;
"""


def _current_run_id(conn: "duckdb.DuckDBPyConnection") -> int:
    row = conn.execute("SELECT max(run_id) FROM analysis_run").fetchone()
    if row is None or row[0] is None:
        raise RuntimeError("Banco sem run — rode `harmonic corpus build` primeiro.")
    return int(row[0])


def _global_axis(fingerprints: dict) -> list[str]:
    """Eixo de funções global (união) para vetores comparáveis no mesmo espaço."""
    keys: set[str] = set()
    for fp in fingerprints.values():
        keys.update(fp.function_distribution)
        keys.update(fp.transition_matrix)
    return sorted(keys)


def _similarity_matrix(song_ids, vectors) -> dict:
    """Cosseno par-a-par (dict simétrico) sobre os vetores no eixo global."""
    sim: dict = {}
    for i, a in enumerate(song_ids):
        for b in song_ids[i + 1:]:
            s = _cosine(vectors[a], vectors[b])
            sim[(a, b)] = s
            sim[(b, a)] = s
    return sim


def _agglomerate(
    song_ids: list[int], sim: dict, k: int, linkage: str = "average"
) -> list[list[int]]:
    """Aglomerativo até `k` clusters. Determinístico.

    Distância entre clusters:
    - `average`: 1 − média das similaridades par-a-par entre membros;
    - `complete`: 1 − MÍNIMO das similaridades (= máxima distância) → famílias
      mais compactas/equilibradas.
    Desempate: menor par de (min song_id, ...) para reprodutibilidade.
    """
    if linkage not in ("average", "complete"):
        raise ValueError(f"linkage inválido: {linkage!r} (use average|complete)")

    clusters: list[list[int]] = [[sid] for sid in song_ids]
    if k >= len(clusters):
        return clusters

    def cluster_dist(ca: list[int], cb: list[int]) -> float:
        sims = [sim[(x, y)] for x in ca for y in cb]
        agg = sum(sims) / len(sims) if linkage == "average" else min(sims)
        return 1.0 - agg

    while len(clusters) > k:
        best = None  # (chave, i, j)
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                dist = cluster_dist(clusters[i], clusters[j])
                key = (dist, min(clusters[i]), min(clusters[j]))
                if best is None or key < best[0]:
                    best = (key, i, j)
        _key, i, j = best
        clusters[i] = clusters[i] + clusters[j]
        clusters.pop(j)
    # Ordena p/ ids de cluster estáveis: por menor song_id do cluster.
    clusters.sort(key=lambda c: min(c))
    return clusters


def _medoid(cluster: list[int], sim: dict) -> int:
    """Música mais central: maior similaridade média com as demais da família."""
    if len(cluster) == 1:
        return cluster[0]

    def avg(x: int) -> float:
        return sum(sim[(x, y)] for y in cluster if y != x) / (len(cluster) - 1)

    # Desempate determinístico por song_id.
    return max(cluster, key=lambda x: (avg(x), -x))


def corpus_baseline(conn: "duckdb.DuckDBPyConnection") -> dict:
    """Participação média por função e taxa por família de cadência (por música).

    O baseline contra o qual o lift de cada família é medido. Computado uma vez.
    """
    song_ids = [
        r[0]
        for r in conn.execute(
            "SELECT song_id FROM v_song_current"
        ).fetchall()
    ]
    return _profile(conn, song_ids)


def _profile(conn: "duckdb.DuckDBPyConnection", song_ids: list[int]) -> dict:
    """Perfil médio de um conjunto de músicas: função (participação) e cadência (taxa/música)."""
    from collections import Counter

    n = len(song_ids) or 1
    fn: Counter = Counter()
    cad: Counter = Counter()
    for sid in song_ids:
        fp = fingerprint_from_db(conn, sid)
        for f, share in fp.function_distribution.items():
            fn[f] += share
        for family, count in fp.cadence_counts.items():
            cad[family] += count
    return {
        "functions": {f: s / n for f, s in fn.items()},   # participação média
        "cadences": {c: v / n for c, v in cad.items()},   # cadências por música
    }


def cluster_traits(
    conn: "duckdb.DuckDBPyConnection",
    song_ids: list[int],
    baseline: dict,
    top: int = 3,
) -> dict:
    """Traços que DISTINGUEM a família: funções/cadências sobre-representadas vs. o corpus.

    lift = participação/taxa média na família − no corpus. Só lift > 0 (o que a
    família tem A MAIS), ordenado desc, com o valor visível. Lista vazia = a família
    é o baseline do corpus (sem traço distintivo). Descritivo, não veredito.
    """
    prof = _profile(conn, song_ids)

    def _lift(kind: str) -> list[tuple[str, float]]:
        base = baseline[kind]
        lifts = [
            (key, share - base.get(key, 0.0))
            for key, share in prof[kind].items()
        ]
        return [
            (k, round(v, 3)) for k, v in sorted(lifts, key=lambda t: -t[1])
            if v > 1e-6
        ][:top]

    return {"functions": _lift("functions"), "cadences": _lift("cadences")}


def build_clusters(
    conn: "duckdb.DuckDBPyConnection", k: int = 8, linkage: str = "average"
) -> dict:
    """Agrupa as músicas do run corrente em `k` famílias e materializa.

    `linkage`: `average` (padrão) ou `complete` (famílias mais equilibradas).
    Idempotente: recomputa só o run corrente. Reusa os embeddings de estilo.
    """
    run_id = _current_run_id(conn)
    song_ids = [
        r[0]
        for r in conn.execute(
            "SELECT song_id FROM v_song_current ORDER BY song_id"
        ).fetchall()
    ]
    fingerprints = {sid: fingerprint_from_db(conn, sid) for sid in song_ids}
    axis = _global_axis(fingerprints)
    vectors = {sid: _feature_vector(fp, axis) for sid, fp in fingerprints.items()}
    sim = _similarity_matrix(song_ids, vectors)

    k = max(1, min(k, len(song_ids)))
    clusters = _agglomerate(song_ids, sim, k, linkage=linkage)

    records: list[tuple] = []
    for cluster_id, members in enumerate(clusters):
        medoid = _medoid(members, sim)
        for sid in members:
            records.append((run_id, sid, cluster_id, sid == medoid))

    conn.execute(_CLUSTER_DDL)
    conn.execute("DELETE FROM song_cluster WHERE run_id = ?", [run_id])
    conn.executemany(
        "INSERT INTO song_cluster (run_id, song_id, cluster_id, is_medoid) "
        "VALUES (?, ?, ?, ?)",
        records,
    )
    conn.execute(_CLUSTER_VIEW)
    return {
        "run_id": run_id,
        "n_songs": len(song_ids),
        "k": len(clusters),
        "linkage": linkage,
        "sizes": sorted((len(c) for c in clusters), reverse=True),
    }
