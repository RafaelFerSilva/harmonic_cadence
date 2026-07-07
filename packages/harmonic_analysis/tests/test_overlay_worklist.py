"""Camada C — materialização da worklist de anomalia + relatório.

Fixture inline (não depende de `cifras/`): materializa 2 músicas, roda o overlay e
valida a spec `functional-anomaly-overlay`:
- a view `v_anomaly_worklist` cobre todas as ocorrências do run e é ordenada;
- a materialização NÃO altera tabelas-base nem as views de gate/ledger (invariância);
- o overlay NÃO reescreve `function_code` (PRATA, nunca ouro);
- o relatório é descritivo (denominador visível) e NUNCA placar.
"""

import textwrap

import pytest

from harmonic_analysis.overlay.materialize import build_anomaly_worklist
from harmonic_analysis.overlay.report import render_anomaly_report
from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus

_FIXTURES = {
    "teste-um": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Dm7` `G7` `C7M` `A7`

        ```
        Dm7 G7 C7M A7
        Dm7 G7 C7M
        ```
        """
    ),
    "teste-dois": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Em7` `A7` `Dm7` `G7` `C7M`

        ```
        Em7 A7 Dm7 G7 C7M
        ```
        """
    ),
}


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("overlay")
    cifras = tmp / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(body, encoding="utf-8")
    c = init_db(str(tmp / "c.duckdb"))
    summary = build_corpus(c, str(cifras / "*.md"))
    assert not summary.get("error")
    return c


def _base_snapshot(conn):
    """Contagens das tabelas-base + gates, para checar invariância pós-overlay."""
    return {
        "occ": conn.execute("SELECT COUNT(*) FROM chord_occurrence").fetchone()[0],
        "occ_fn": conn.execute(
            "SELECT COUNT(*) FROM chord_occurrence WHERE function_code IS NOT NULL"
        ).fetchone()[0],
        "fn_hash": conn.execute(
            "SELECT SUM(hash(song_id || position || COALESCE(function_code,''))) "
            "FROM chord_occurrence"
        ).fetchone()[0],
        "gate_dim": conn.execute("SELECT COUNT(*) FROM v_gate_diminished").fetchone()[0],
        "gate_d2": conn.execute("SELECT COUNT(*) FROM v_gate_d2").fetchone()[0],
        "gate_cad": conn.execute("SELECT COUNT(*) FROM v_gate_cadence").fetchone()[0],
    }


def test_worklist_covers_all_current_run_occurrences(conn):
    before = conn.execute(
        "SELECT COUNT(*) FROM chord_occurrence o JOIN v_song_current s "
        "ON o.song_id = s.song_id"
    ).fetchone()[0]
    summary = build_anomaly_worklist(conn)
    assert summary["n_occurrences"] == before
    n_view = conn.execute("SELECT COUNT(*) FROM v_anomaly_worklist").fetchone()[0]
    assert n_view == before


def test_worklist_ordered_by_surprise_desc(conn):
    build_anomaly_worklist(conn)
    bits = [
        r[0]
        for r in conn.execute(
            "SELECT surprise_bits FROM v_anomaly_worklist"
        ).fetchall()
    ]
    assert bits == sorted(bits, reverse=True)


def test_surprise_is_finite_and_positive(conn):
    build_anomaly_worklist(conn)
    row = conn.execute(
        "SELECT MIN(surprise_bits), MAX(surprise_bits) FROM v_anomaly_worklist"
    ).fetchone()
    assert row[0] is not None and row[0] > 0
    assert row[1] < float("inf")


def test_materialization_does_not_touch_base_or_gates(conn):
    """Invariância: tabelas-base e gates idênticos antes/depois do overlay (PRATA)."""
    before = _base_snapshot(conn)
    build_anomaly_worklist(conn)
    after = _base_snapshot(conn)
    assert before == after, "overlay alterou tabela-base ou gate — viola PRATA"


def test_rebuild_is_idempotent(conn):
    """Rematerializar o mesmo run não duplica escores nem muda a ordenação."""
    build_anomaly_worklist(conn)
    n1 = conn.execute("SELECT COUNT(*) FROM anomaly_score").fetchone()[0]
    top1 = conn.execute(
        "SELECT song_id, position FROM v_anomaly_worklist LIMIT 3"
    ).fetchall()
    build_anomaly_worklist(conn)
    n2 = conn.execute("SELECT COUNT(*) FROM anomaly_score").fetchone()[0]
    top2 = conn.execute(
        "SELECT song_id, position FROM v_anomaly_worklist LIMIT 3"
    ).fetchall()
    assert n1 == n2
    assert top1 == top2


def test_report_shows_denominators(conn):
    build_anomaly_worklist(conn)
    md = render_anomaly_report(conn)
    assert "n(trigrama)" in md and "n(contexto)" in md
    assert "Ocorrências pontuadas" in md


def test_report_is_descriptive_never_scoreboard(conn):
    """Guarda-corpo anti-placar (herdado do corpus report): overlay é PRATA."""
    build_anomaly_worklist(conn)
    md = render_anomaly_report(conn).lower()
    assert "rankeia" in md and "adjudica" in md
    assert "worklist de curadoria" in md
    for forbidden in ["acerto", "acurácia", "acuracia", "accuracy",
                      "taxa de erro", "precisão do modelo", "f1"]:
        assert forbidden not in md, f"vocabulário de placar proibido: {forbidden}"
