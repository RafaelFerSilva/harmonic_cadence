"""Materializa a worklist de anomalia funcional no DuckDB.

AUTO-CONTIDO e ADITIVO: cria a tabela `anomaly_score` e a view `v_anomaly_worklist`
sob demanda (não toca `schema.sql`/`views.sql` base). Rollback = DROP das duas.
Deriva/regenerável: carimba o `run_id`/`engine_version` de origem e falha-rápido se o
run corrente não existir.

O overlay é PRATA: só LÊ `function_code` (rótulo do coder) e ESCREVE surpresa. Nunca
altera `chord_occurrence` nem qualquer view de gate/ledger.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harmonic_analysis.overlay.model import BidirectionalModel

if TYPE_CHECKING:
    import duckdb

# `∅` = grau ausente (acorde sem grau diatônico) — token informativo, 1ª classe.
_NO_DEGREE = "∅"

_SCORE_DDL = """
CREATE TABLE IF NOT EXISTS anomaly_score (
    run_id             INTEGER,
    song_id            INTEGER,
    position           INTEGER,
    function_code      VARCHAR,
    degree             VARCHAR,
    surprise_bits      DOUBLE,  -- combinado = média(função, grau)
    surprise_function  DOUBLE,  -- bilateral, canal de função
    surprise_degree    DOUBLE,  -- bilateral, canal de grau
    PRIMARY KEY (run_id, song_id, position)
);
"""

# Colunas que a v2 acrescenta — se a tabela v1 existir sem elas, recriamos (derivado).
_V2_COLUMNS = {"degree", "surprise_function", "surprise_degree"}

# Worklist = escores do run corrente + o acorde/símbolo + marcas de interseção com
# as worklists de curadoria já existentes (trítono não-dominante; centro divergente).
_WORKLIST_DDL = """
CREATE OR REPLACE VIEW v_anomaly_worklist AS
SELECT
    a.song_id,
    s.title,
    a.position,
    o.symbol,
    a.function_code,
    a.degree,
    a.surprise_bits,
    a.surprise_function,
    a.surprise_degree,
    (t.song_id IS NOT NULL)               AS in_tritone_ledger,
    (s.center_status = 'diverge')         AS in_center_diverge,
    s.completeness
FROM anomaly_score a
JOIN v_song_current s      ON a.song_id = s.song_id AND a.run_id = s.run_id
JOIN chord_occurrence o    ON o.song_id = a.song_id AND o.position = a.position
LEFT JOIN v_ledger_tritone_nondominant t
       ON t.song_id = a.song_id AND t.position = a.position
ORDER BY a.surprise_bits DESC, a.song_id, a.position;
"""


def _current_run_id(conn: "duckdb.DuckDBPyConnection") -> int:
    row = conn.execute("SELECT max(run_id) FROM analysis_run").fetchone()
    if row is None or row[0] is None:
        raise RuntimeError("Banco sem run — rode `harmonic corpus build` primeiro.")
    return int(row[0])


def build_anomaly_worklist(
    conn: "duckdb.DuckDBPyConnection", order: int = 3
) -> dict:
    """Treina o LM sobre o run corrente e materializa `anomaly_score` + a view.

    Devolve um resumo (run_id, nº de ocorrências, nº de músicas). Idempotente:
    recomputa só o run corrente (apaga escores antigos do MESMO run).
    """
    run_id = _current_run_id(conn)

    # Sequências por música, em ordem de position (escopo = run corrente). Dois
    # canais: função e grau (NULL → sentinela ∅, informativo).
    rows = conn.execute(
        """
        SELECT o.song_id, o.position, o.function_code, o.degree
        FROM chord_occurrence o
        JOIN v_song_current s ON o.song_id = s.song_id
        ORDER BY o.song_id, o.position
        """
    ).fetchall()

    sequences: dict[int, list[tuple[int, str, str]]] = {}
    for song_id, position, fn, deg in rows:
        sequences.setdefault(song_id, []).append(
            (position, fn, deg if deg is not None else _NO_DEGREE)
        )

    fn_model = BidirectionalModel(order=order).fit(
        [[fn for _p, fn, _d in seq] for seq in sequences.values()]
    )
    deg_model = BidirectionalModel(order=order).fit(
        [[d for _p, _fn, d in seq] for seq in sequences.values()]
    )

    records: list[tuple] = []
    for song_id, seq in sequences.items():
        fn_bits = fn_model.score_sequence([fn for _p, fn, _d in seq])
        deg_bits = deg_model.score_sequence([d for _p, _fn, d in seq])
        for (position, fn, deg), sf, sd in zip(seq, fn_bits, deg_bits):
            combined = (sf + sd) / 2.0
            records.append(
                (run_id, song_id, position, fn, deg, combined, sf, sd)
            )

    # Rebuild derivado: se a tabela v1 existir sem as colunas da v2, recria (sem perda).
    _ensure_score_schema(conn)
    conn.execute("DELETE FROM anomaly_score WHERE run_id = ?", [run_id])
    conn.executemany(
        "INSERT INTO anomaly_score "
        "(run_id, song_id, position, function_code, degree, surprise_bits, "
        " surprise_function, surprise_degree) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        records,
    )
    conn.execute(_WORKLIST_DDL)

    return {
        "run_id": run_id,
        "n_occurrences": len(records),
        "n_songs": len(sequences),
        "order": order,
    }


def _ensure_score_schema(conn: "duckdb.DuckDBPyConnection") -> None:
    """Cria `anomaly_score`; se a tabela v1 (sem colunas v2) existir, recria-a.

    A tabela é derivada/regenerável — dropá-la não perde nada (o run é recomputado).
    """
    existing = {
        r[0]
        for r in conn.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'anomaly_score'"
        ).fetchall()
    }
    if existing and not _V2_COLUMNS.issubset(existing):
        conn.execute("DROP TABLE anomaly_score")
    conn.execute(_SCORE_DDL)


# ═══ Draft de adjudicação por precedente (CBR) — ADITIVO, PRATA ══════════════
# Materializa os vereditos DRAFT das ocorrências PENDENTES (ainda sem veredito
# humano) dos ledgers de trítono e centro. Tabela + view derivadas/regeneráveis;
# rollback = DROP das duas. Drafts NUNCA contam como adjudicação: a auditoria
# anti-drift e o denominador de completude ignoram esta tabela.
_DRAFT_DDL = """
CREATE TABLE IF NOT EXISTS draft_verdict (
    run_id          INTEGER,
    ledger          VARCHAR,   -- 'tritone' | 'center'
    slug            VARCHAR,
    position        INTEGER,   -- NULL p/ centro (grão de música)
    draft_verdict   VARCHAR,   -- herdado do precedente mais próximo (ou 'ambiguous')
    chediak_page    INTEGER,   -- herdado do precedente; NULL p/ ambiguous
    confidence      DOUBLE,    -- concordância dos k vizinhos
    denominator     INTEGER,   -- k efetivo
    nearest_slug    VARCHAR,   -- o precedente mais próximo (auditável)
    nearest_dist    DOUBLE,
    status          VARCHAR DEFAULT 'draft',
    PRIMARY KEY (run_id, ledger, slug, position)
);
"""

_DRAFT_VIEW = """
CREATE OR REPLACE VIEW v_draft_verdict AS
SELECT run_id, ledger, slug, position, draft_verdict, chediak_page,
       confidence, denominator, nearest_slug, nearest_dist, status
FROM draft_verdict
WHERE run_id = (SELECT max(run_id) FROM analysis_run)
ORDER BY ledger, confidence DESC, slug;
"""


def build_draft_verdicts(
    conn: "duckdb.DuckDBPyConnection", k: int = 5
) -> dict:
    """Rascunha por precedente as ocorrências PENDENTES dos dois ledgers.

    Pendente = no ledger mas sem veredito humano (`verdict`/`winner` NULL). A base de
    casos são SÓ os vereditos confirmados (o CBR nunca usa draft como precedente).
    Idempotente: recomputa o run corrente. Aditivo: não toca nenhuma tabela canônica.
    """
    from harmonic_analysis.corpus.modal_centers import Citation  # noqa: F401
    from harmonic_analysis.overlay.precedent import (
        center_geometry,
        draft_verdict,
        load_case_base,
        tritone_geometry,
    )

    run_id = _current_run_id(conn)
    conn.execute(_DRAFT_DDL)
    conn.execute("DELETE FROM draft_verdict WHERE run_id = ?", [run_id])

    records: list[tuple] = []

    # ── Trítono: ocorrências do ledger sem veredito (grão de ocorrência) ─────
    tri_base = load_case_base(conn, "tritone")
    tri_pending = conn.execute(
        "SELECT l.song_id, l.position, s.slug "
        "FROM v_ledger_tritone_nondominant l "
        "JOIN v_song_current s ON l.song_id = s.song_id "
        "WHERE l.verdict IS NULL"
    ).fetchall()
    for song_id, position, slug in tri_pending:
        d = draft_verdict(
            tritone_geometry(conn, song_id, position),
            tri_base, ledger="tritone", key=(slug, position), k=k,
        )
        page = d.citation.page if d.citation is not None else None
        near = d.neighbors[0][0].slug if d.neighbors else None
        records.append((run_id, "tritone", slug, position, d.verdict, page,
                        d.confidence, d.denominator, near, d.nearest_distance))

    # ── Centro: músicas `diverge` sem veredito (grão de música) ──────────────
    ctr_base = load_case_base(conn, "center")
    ctr_pending = conn.execute(
        "SELECT song_id, slug FROM v_center_worklist WHERE winner IS NULL"
    ).fetchall()
    for song_id, slug in ctr_pending:
        d = draft_verdict(
            center_geometry(conn, song_id),
            ctr_base, ledger="center", key=(slug,), k=k,
        )
        page = d.citation.page if d.citation is not None else None
        near = d.neighbors[0][0].slug if d.neighbors else None
        records.append((run_id, "center", slug, None, d.verdict, page,
                        d.confidence, d.denominator, near, d.nearest_distance))

    if records:
        conn.executemany(
            "INSERT INTO draft_verdict (run_id, ledger, slug, position, draft_verdict, "
            "chediak_page, confidence, denominator, nearest_slug, nearest_dist) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            records,
        )
    conn.execute(_DRAFT_VIEW)
    return {
        "run_id": run_id,
        "n_drafts": len(records),
        "n_tritone_pending": len(tri_pending),
        "n_center_pending": len(ctr_pending),
        "k": k,
    }
