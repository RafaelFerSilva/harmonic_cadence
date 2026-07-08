"""Camada C Fase 1 — assistente de adjudicação por precedente (CBR).

Valida a spec `adjudication-precedent-assist`:
- geometria transposição-invariante (mesma progressão em tons diferentes → distância 0);
- retrieval k-NN: top-k por distância, auto-precedente excluído, base só confirmados;
- veredito DRAFT: herda veredito+citação do +próximo; confiança = concordância; precedente
  ambíguo/distante → draft ambiguous sem citação;
- invariância PRATA: materializar drafts não altera `function_code`/gates; rollback limpo;
- ii-V: os 3 conhecidos aparecem (integração no corpus real, guardada).
"""

import os
import textwrap

import pytest

from harmonic_analysis.corpus.modal_centers import Citation
from harmonic_analysis.overlay import precedent as P
from harmonic_analysis.overlay.precedent import (
    PrecedentCase,
    draft_verdict,
    feature_distance,
    tritone_geometry,
)
from harmonic_analysis.persistence.db import init_db
from harmonic_analysis.persistence.materialize import build_corpus


# ── Fixtures de progressão: MESMO G7 (trítono) em Dó e em Ré ─────────────────
_FIXTURES = {
    "prog-em-do": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Dm7` `G7` `C7M`

        ```
        Dm7 G7 C7M
        Dm7 G7 C7M
        ```
        """
    ),
    "prog-em-re": textwrap.dedent(
        """\
        **Acordes Utilizados:** `Em7` `A7` `D7M`

        ```
        Em7 A7 D7M
        Em7 A7 D7M
        ```
        """
    ),
}


@pytest.fixture(scope="module")
def conn(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("precedent")
    cifras = tmp / "cifras"
    cifras.mkdir()
    for name, body in _FIXTURES.items():
        (cifras / f"{name}.md").write_text(body, encoding="utf-8")
    c = init_db(str(tmp / "c.duckdb"))
    summary = build_corpus(c, str(cifras / "*.md"))
    assert not summary.get("error")
    return c


def _pos_of(conn, slug, symbol):
    sid = conn.execute(
        "SELECT song_id FROM v_song_current WHERE slug = ?", [slug]
    ).fetchone()[0]
    return sid, conn.execute(
        "SELECT position FROM chord_occurrence WHERE song_id = ? AND symbol = ? "
        "ORDER BY position LIMIT 1",
        [sid, symbol],
    ).fetchone()[0]


# ── feature_distance (puro) ──────────────────────────────────────────────────
def test_feature_distance_identical_is_zero():
    g = {"function": ("cat", "D"), "root_to_tonic": ("cyc", 7)}
    assert feature_distance(g, g) == 0.0


def test_feature_distance_categorical_mismatch():
    a = {"function": ("cat", "D")}
    b = {"function": ("cat", "Emp")}
    assert feature_distance(a, b) == 1.0


def test_feature_distance_cyclic_is_circular():
    # 0 vs 6 semitons = meia-volta = distância máxima (6/6 = 1.0).
    a = {"x": ("cyc", 0)}
    b = {"x": ("cyc", 6)}
    assert feature_distance(a, b) == pytest.approx(1.0)
    # 0 vs 11 = 1 semitom pelo caminho curto (1/6), não 11.
    assert feature_distance({"x": ("cyc", 0)}, {"x": ("cyc", 11)}) == pytest.approx(1 / 6)


def test_feature_distance_no_shared_keys_is_max():
    assert feature_distance({"a": ("cat", "x")}, {"b": ("cat", "y")}) == 1.0


# ── Geometria transposição-invariante (DB) ───────────────────────────────────
def test_geometry_transposition_invariant(conn):
    sid_do, pos_do = _pos_of(conn, "prog-em-do", "G7")
    sid_re, pos_re = _pos_of(conn, "prog-em-re", "A7")
    g_do = tritone_geometry(conn, sid_do, pos_do)
    g_re = tritone_geometry(conn, sid_re, pos_re)
    # Mesmo ii-V-I em tons diferentes → geometria idêntica → distância 0.
    assert feature_distance(g_do, g_re) == 0.0


def test_geometry_missing_occurrence_fails_visible(conn):
    sid = conn.execute("SELECT song_id FROM v_song_current LIMIT 1").fetchone()[0]
    with pytest.raises(ValueError):
        tritone_geometry(conn, sid, 9999)


# ── draft_verdict (puro, base sintética) ─────────────────────────────────────
_CIT = Citation(source="Almir Chediak, Harmonia & Improvisação", volume=1, page=116)


def _case(key, verdict, geom, cit=None):
    return PrecedentCase(
        key=key, slug=key[0], symbol="X", verdict=verdict, citation=cit,
        note="nota", geometry=geom,
    )


def test_draft_inherits_nearest_verdict_and_citation():
    suspect = {"function": ("cat", "Emp"), "root_to_tonic": ("cyc", 6)}
    base = [
        _case(("near", 1), "chromatic_approach", suspect, _CIT),          # dist 0
        _case(("far", 1), "emp_legitimate",
              {"function": ("cat", "T"), "root_to_tonic": ("cyc", 0)}),
    ]
    d = draft_verdict(suspect, base, ledger="tritone", key=("suspect", 1), k=5)
    assert d.verdict == "chromatic_approach"
    assert d.citation is _CIT
    assert d.status == "draft"


def test_draft_confidence_is_neighbor_agreement():
    g = {"function": ("cat", "Emp")}
    base = [
        _case(("a", 1), "chromatic_approach", g, _CIT),
        _case(("b", 1), "chromatic_approach", g, _CIT),
        _case(("c", 1), "emp_legitimate", g, _CIT),
    ]
    d = draft_verdict(g, base, ledger="tritone", key=("s", 1), k=3)
    assert d.verdict == "chromatic_approach"
    assert d.denominator == 3
    assert d.confidence == pytest.approx(2 / 3)


def test_draft_nearest_ambiguous_gives_ambiguous_without_citation():
    g = {"function": ("cat", "Emp")}
    base = [_case(("a", 1), "ambiguous", g)]  # +próximo é ambíguo
    d = draft_verdict(g, base, ledger="tritone", key=("s", 1), k=5)
    assert d.verdict == "ambiguous"
    assert d.citation is None


def test_draft_distant_precedent_falls_to_ambiguous():
    suspect = {"function": ("cat", "Emp"), "root_to_tonic": ("cyc", 0)}
    far = {"function": ("cat", "T"), "root_to_tonic": ("cyc", 6)}  # dist alta
    base = [_case(("a", 1), "chromatic_approach", far, _CIT)]
    d = draft_verdict(suspect, base, ledger="tritone", key=("s", 1), k=5, cutoff=0.5)
    assert d.verdict == "ambiguous"
    assert d.citation is None


def test_draft_excludes_self_precedent():
    g = {"function": ("cat", "Emp")}
    base = [
        _case(("s", 1), "emp_legitimate", g, _CIT),          # a PRÓPRIA ocorrência
        _case(("other", 1), "chromatic_approach", g, _CIT),
    ]
    d = draft_verdict(g, base, ledger="tritone", key=("s", 1), k=5)
    # Não pode herdar de si mesma; herda do 'other'.
    assert d.verdict == "chromatic_approach"


def test_draft_empty_base_is_ambiguous():
    d = draft_verdict({"function": ("cat", "Emp")}, [], ledger="tritone",
                      key=("s", 1), k=5)
    assert d.verdict == "ambiguous"
    assert d.denominator == 0


# ── Base de casos só confirmados + PRATA + materialização (DB) ────────────────
def test_case_base_only_present_slugs(conn):
    # No fixture minúsculo nenhum slug das adjudicações reais existe → base vazia.
    assert P.load_case_base(conn, "tritone") == []
    assert P.load_case_base(conn, "center") == []


def test_materialize_is_prata_and_additive(conn):
    from harmonic_analysis.overlay.materialize import build_draft_verdicts

    before = conn.execute(
        "SELECT song_id, position, function_code FROM chord_occurrence ORDER BY 1,2"
    ).fetchall()
    summary = build_draft_verdicts(conn, k=5)
    after = conn.execute(
        "SELECT song_id, position, function_code FROM chord_occurrence ORDER BY 1,2"
    ).fetchall()
    # PRATA: nenhum function_code tocado.
    assert before == after
    # View existe e é regenerável/rollback limpo.
    conn.execute("SELECT * FROM v_draft_verdict")
    conn.execute("DROP VIEW v_draft_verdict")
    assert before == conn.execute(
        "SELECT song_id, position, function_code FROM chord_occurrence ORDER BY 1,2"
    ).fetchall()
    assert "n_drafts" in summary


# ── Integração no corpus real (guardada — corpus.duckdb é gerado/gitignored) ──
_REAL_DB = os.path.join(os.getcwd(), "corpus.duckdb")


@pytest.mark.skipif(not os.path.exists(_REAL_DB), reason="corpus.duckdb ausente")
def test_ii_v_known_three_present_on_real_corpus():
    import duckdb

    c = duckdb.connect(_REAL_DB, read_only=True)
    try:
        slugs = {d["slug"] for d in P.ii_v_trap_candidates(c)}
    finally:
        c.close()
    assert {"bolinha-de-sabao", "menina", "rio"} <= slugs


@pytest.mark.skipif(not os.path.exists(_REAL_DB), reason="corpus.duckdb ausente")
def test_leave_one_out_runs_and_is_descriptive(conn=None):
    import duckdb

    c = duckdb.connect(_REAL_DB, read_only=True)
    try:
        loo = P.leave_one_out(c, "tritone", k=10)
    finally:
        c.close()
    # Descritivo: a taxa é uma fração válida; o denominador é o nº de casos confirmados.
    assert loo["n"] > 0
    assert 0.0 <= loo["rate"] <= 1.0
    assert loo["agree"] == sum(1 for case, d in loo["drafts"] if d.verdict == case.verdict)
