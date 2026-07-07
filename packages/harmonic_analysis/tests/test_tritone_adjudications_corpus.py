"""Invariante do corpus de vereditos de trítono — a citação como gate.

Espelha `test_modal_centers_corpus`: nenhum veredito decisivo pode existir sem uma
`Citation` válida; `ambiguous` exige nota; o `verdict` é restrito ao enum fechado.
Defesa em profundidade sobre o `__post_init__` (runtime) + `Literal` (IDE/mypy).
"""

import pytest

from harmonic_analysis.corpus import Citation
from harmonic_analysis.corpus.tritone_adjudications import (
    ADJUDICATIONS,
    TritoneVerdict,
    lookup_tritone_verdict,
)

_CIT = Citation(source="Almir Chediak, Harmonia & Improvisação", volume=1, page=114)


@pytest.mark.parametrize(
    "adj", ADJUDICATIONS, ids=lambda a: f"{a.slug}:{a.position}"
)
def test_decisive_verdicts_carry_a_valid_citation(adj):
    if adj.verdict == "ambiguous":
        assert adj.note.strip()  # ambíguo declara o porquê
    else:
        assert isinstance(adj.citation, Citation)
        assert adj.citation.source.strip()
        assert adj.citation.page >= 1


@pytest.mark.parametrize(
    "adj", ADJUDICATIONS, ids=lambda a: f"{a.slug}:{a.position}"
)
def test_identity_is_unique(adj):
    # Cada (slug, position) aparece uma vez no índice (sem colisão de chave).
    assert lookup_tritone_verdict(adj.slug, adj.position) is adj


def test_decisive_verdict_without_citation_fails_fast():
    with pytest.raises(ValueError):
        TritoneVerdict(
            slug="x",
            position=1,
            symbol="Ab7(#11)",
            verdict="subv",
            note="geometria",
            citation=None,
        )


def test_ambiguous_without_note_fails_fast():
    with pytest.raises(ValueError):
        TritoneVerdict(
            slug="x",
            position=1,
            symbol="Bb7",
            verdict="ambiguous",
            note="   ",
        )


def test_verdict_outside_enum_fails_fast():
    with pytest.raises(ValueError):
        TritoneVerdict(
            slug="x",
            position=1,
            symbol="Bb7",
            verdict="modal_borrowing",  # não está no enum fechado
            note="n",
            citation=_CIT,
        )


def test_negative_position_fails_fast():
    with pytest.raises(ValueError):
        TritoneVerdict(
            slug="x",
            position=-1,
            symbol="Bb7",
            verdict="emp_legitimate",
            note="n",
            citation=_CIT,
        )


def test_ambiguous_needs_no_citation():
    adj = TritoneVerdict(
        slug="flora",
        position=27,
        symbol="C#74(9)",
        verdict="ambiguous",
        note="centro tonal instável (None) — grau irrecuperável.",
    )
    assert adj.verdict == "ambiguous"
    assert adj.citation is None


def test_lookup_resolves_slug_variants():
    adj = TritoneVerdict(
        slug="Bye Bye Brasil",
        position=29,
        symbol="Bb7(9)",
        verdict="emp_legitimate",
        note="bVII7 → Em7 (repouso).",
        citation=_CIT,
    )
    # o índice do CORPUS usa slugify; o lookup também — variantes resolvem.
    assert adj.key == ("bye-bye-brasil", 29)


def test_unknown_occurrence_misses_cleanly():
    assert lookup_tritone_verdict("nao-existe", 999) is None
