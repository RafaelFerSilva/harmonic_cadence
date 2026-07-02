"""corpus-completeness — invariantes do ledger curado (evidência obrigatória)."""

import pytest

from harmonic_analysis.corpus.completeness import (
    COMPLETENESS_LEDGER,
    CompletenessFact,
    completeness_for,
)


def test_fact_without_evidence_fails_fast():
    with pytest.raises(ValueError, match="evidência"):
        CompletenessFact(
            slug="x", status="suspect", missing_declared=("C7",), evidence="  "
        )


def test_fact_without_missing_chords_fails_fast():
    with pytest.raises(ValueError, match="ausentes"):
        CompletenessFact(
            slug="x", status="suspect", missing_declared=(), evidence="fonte"
        )


def test_invalid_status_fails_fast():
    with pytest.raises(ValueError, match="status"):
        CompletenessFact(
            slug="x", status="complete", missing_declared=("C7",), evidence="fonte"
        )


def test_lookup_defaults_to_complete():
    assert completeness_for("slug-que-nao-existe") == "complete"
    assert completeness_for("a-paz") == "incomplete"
    assert completeness_for("dindi") == "suspect"


def test_ledger_facts_are_wellformed():
    """Todo fato do ledger tem evidência, ausentes e status válido (o __post_init__
    já garante; isto trava a importação como gate)."""
    assert len(COMPLETENESS_LEDGER) >= 20
    for slug, fact in COMPLETENESS_LEDGER.items():
        assert fact.slug == slug
        assert fact.missing_declared and fact.evidence.strip()


def test_ledger_carries_only_chord_symbols():
    """Fronteira de copyright: os dados curados são só símbolos de acorde (gramática
    de acorde válida ou prefixo-de-acorde do dialeto da fonte) — nunca letra/verso."""
    from cifra_core import ChordPattern

    for fact in COMPLETENESS_LEDGER.values():
        for sym in fact.missing_declared:
            assert " " not in sym, f"{fact.slug}: {sym!r} contém espaço (não é símbolo)"
            assert ChordPattern.CHORD.match(sym), (
                f"{fact.slug}: {sym!r} não parece símbolo de acorde"
            )


# ── estampagem na persistência + visibilidade no report ─────────────────────


def test_materialize_stamps_completeness(tmp_path, monkeypatch):
    """Slug no ledger → song.completeness estampado; fora → 'complete'.
    Gates continuam avaliando ocorrências de músicas quarentenadas."""
    import textwrap

    from harmonic_analysis.persistence.db import init_db
    from harmonic_analysis.persistence.materialize import build_corpus
    from harmonic_analysis.persistence.report import render_report

    cifras = tmp_path / "cifras"
    cifras.mkdir()
    body = textwrap.dedent(
        """\
        **Acordes Utilizados:** `Dm7` `G7` `C7M`

        ```
        Dm7 G7 C7M
        Dm7 G7 C7M
        ```
        """
    )
    (cifras / "dindi.md").write_text(body, encoding="utf-8")       # no ledger: suspect
    (cifras / "musica-limpa.md").write_text(body, encoding="utf-8")  # fora: complete
    conn = init_db(str(tmp_path / "c.duckdb"))
    build_corpus(conn, str(cifras / "*.md"))

    rows = dict(
        conn.execute("SELECT slug, completeness FROM v_song_current").fetchall()
    )
    assert rows == {"dindi": "suspect", "musica-limpa": "complete"}

    # gates NÃO filtram: as ocorrências da música quarentenada estão nas views base
    n_occ_q = conn.execute(
        "SELECT COUNT(*) FROM chord_occurrence o JOIN v_song_current s "
        "ON o.song_id=s.song_id WHERE s.slug='dindi'"
    ).fetchone()[0]
    # (linhas consecutivas idênticas são deduplicadas pelo clean_cifra_lines → 3)
    assert n_occ_q == 3  # todas avaliáveis

    md = render_report(conn)
    assert "Completude do DADO DE ENTRADA" in md
    assert "suspect=1" in md and "complete=1" in md
