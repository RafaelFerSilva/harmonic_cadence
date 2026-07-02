"""corpus-analytics — views de analytics e relatório Markdown descritivo.

Fixture inline (sem depender de `cifras/`): materializa 2 músicas e valida a
forma das views, a normalização de grau da view de padrões e o render do
relatório (6 seções, linguagem descritiva — nunca placar)."""

import textwrap

import pytest

from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus
from harmonic_analysis.persistence.report import render_report

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
    tmp = tmp_path_factory.mktemp("corpus")
    cifras = tmp / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(body, encoding="utf-8")
    c = init_db(str(tmp / "c.duckdb"))
    summary = build_corpus(c, str(cifras / "*.md"))
    assert not summary.get("error")
    return c


def test_cadence_distribution_shape(conn):
    rows = conn.execute(
        "SELECT family, instances, songs FROM v_cadence_distribution"
    ).fetchall()
    assert rows, "fixture tem ii-V-I → deve haver cadências"
    for family, instances, songs in rows:
        assert instances >= songs >= 1  # instâncias ≥ músicas distintas


def test_function_trigram_counts(conn):
    rows = conn.execute("SELECT fn1, fn2, fn3, n FROM v_function_trigram").fetchall()
    # 7+5 acordes → 5+3 = 8 janelas de trigrama no total.
    assert sum(r[3] for r in rows) == 8


def test_vocab_by_mode_covers_all_occurrences(conn):
    total = conn.execute("SELECT SUM(n) FROM v_vocab_by_mode").fetchone()[0]
    n_occ = conn.execute("SELECT COUNT(*) FROM chord_occurrence").fetchone()[0]
    assert total == n_occ


def test_secondary_density_bounds(conn):
    rows = conn.execute(
        "SELECT secondary_count, n_chords, secondary_pct FROM v_secondary_density"
    ).fetchall()
    assert len(rows) == 2  # uma linha por música (LEFT JOIN em song)
    for count, n_chords, pct in rows:
        assert 0 <= count <= n_chords
        assert pct is None or 0 <= pct <= 100


def test_ledger_pattern_degree_normalization(conn):
    """A normalização SQL espelha `degree_base`: acidente inicial + numeral, caixa-alta."""
    from harmonic_analysis.domain.harmonic_function import degree_base

    # Compara sobre os graus DISTINTOS realmente presentes no banco.
    degrees = [
        r[0]
        for r in conn.execute(
            "SELECT DISTINCT degree FROM chord_occurrence WHERE degree IS NOT NULL"
        ).fetchall()
    ]
    for d in degrees:
        sql = conn.execute(
            "SELECT COALESCE(NULLIF(upper(regexp_extract(?, "
            "'(?i)^[b#]?(vii|vi|iv|v|iii|ii|i)', 1)), ''), '?')",
            [d],
        ).fetchone()[0]
        assert sql == (degree_base(d) or "?"), f"grau {d!r}: SQL={sql}"


def test_report_has_six_sections(conn):
    md = render_report(conn)
    for heading in [
        "## 1. Corpus e proveniência",
        "## 2. Cadências",
        "## 3. Progressões funcionais",
        "## 4. Vocabulário de qualidades por modo",
        "## 5. Dominantes secundários",
        "## 6. Worklist de curadoria",
    ]:
        assert heading in md, heading


def test_report_is_descriptive_never_scoreboard(conn):
    """Guarda-corpo da spec: linguagem descritiva, nunca placar do motor."""
    md = render_report(conn).lower()
    for forbidden in ("acerto", "acurácia", "accuracy", "taxa de erro"):
        assert forbidden not in md, forbidden
    assert "worklist de curadoria" in md
    assert "não placar" in md or "nada aqui é placar" in md


def test_views_scope_to_current_run(tmp_path):
    """Dois builds no mesmo banco: gates/ledger/analytics respondem SÓ pelo run
    corrente (sem o escopo, os snapshots somavam — ledger dobrado)."""
    from harmonic_analysis.persistence.materialize import build_corpus as _build

    cifras = tmp_path / "cifras"
    cifras.mkdir()
    (cifras / "t.md").write_text(_FIXTURES["teste-um"], encoding="utf-8")
    conn2 = init_db(str(tmp_path / "c.duckdb"))
    _build(conn2, str(cifras / "*.md"))
    _build(conn2, str(cifras / "*.md"))  # segundo snapshot, mesmo corpus

    assert conn2.execute("SELECT COUNT(*) FROM song").fetchone()[0] == 2  # histórico
    assert conn2.execute("SELECT COUNT(*) FROM v_song_current").fetchone()[0] == 1
    n_ledger = conn2.execute(
        "SELECT SUM(n) FROM v_center_ledger"
    ).fetchone()[0]
    assert n_ledger == 1  # não soma runs
    md = render_report(conn2)
    assert "Músicas: **1**" in md
