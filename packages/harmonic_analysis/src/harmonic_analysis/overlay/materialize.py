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

from harmonic_analysis.overlay.model import FunctionalSequenceModel

if TYPE_CHECKING:
    import duckdb


_SCORE_DDL = """
CREATE TABLE IF NOT EXISTS anomaly_score (
    run_id         INTEGER,
    song_id        INTEGER,
    position       INTEGER,
    function_code  VARCHAR,
    surprise_bits  DOUBLE,
    ngram_count    INTEGER,
    context_count  INTEGER,
    PRIMARY KEY (run_id, song_id, position)
);
"""

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
    a.surprise_bits,
    a.ngram_count,
    a.context_count,
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

    # Sequências por música, em ordem de position (escopo = run corrente).
    rows = conn.execute(
        """
        SELECT o.song_id, o.position, o.function_code
        FROM chord_occurrence o
        JOIN v_song_current s ON o.song_id = s.song_id
        ORDER BY o.song_id, o.position
        """
    ).fetchall()

    sequences: dict[int, list[tuple[int, str]]] = {}
    for song_id, position, fn in rows:
        sequences.setdefault(song_id, []).append((position, fn))

    model = FunctionalSequenceModel(order=order)
    model.fit([[fn for _pos, fn in seq] for seq in sequences.values()])

    records: list[tuple] = []
    for song_id, seq in sequences.items():
        codes = [fn for _pos, fn in seq]
        for (position, _fn), sc in zip(seq, model.score_sequence(codes)):
            records.append(
                (
                    run_id,
                    song_id,
                    position,
                    sc.function_code,
                    sc.surprise_bits,
                    sc.ngram_count,
                    sc.context_count,
                )
            )

    conn.execute(_SCORE_DDL)
    conn.execute("DELETE FROM anomaly_score WHERE run_id = ?", [run_id])
    conn.executemany(
        "INSERT INTO anomaly_score "
        "(run_id, song_id, position, function_code, surprise_bits, "
        " ngram_count, context_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
        records,
    )
    conn.execute(_WORKLIST_DDL)

    return {
        "run_id": run_id,
        "n_occurrences": len(records),
        "n_songs": len(sequences),
        "order": order,
    }
