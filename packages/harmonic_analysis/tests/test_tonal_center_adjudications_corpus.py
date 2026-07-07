"""Invariante do corpus de vereditos de centro tonal — a citação como gate.

Espelha `test_tritone_adjudications_corpus`: nenhum veredito decisivo sem `Citation`
válida; `ambiguous` dispensa citação mas exige evidência; `winner` restrito ao enum.
"""

import pytest

from harmonic_analysis.corpus import Citation
from harmonic_analysis.corpus.tonal_center_adjudications import (
    ADJUDICATIONS,
    _DECISIVE,
    TonalCenterVerdict,
    lookup_center_verdict,
)

_CIT = Citation(source="Almir Chediak, Harmonia & Improvisação", volume=1, page=84)


@pytest.mark.parametrize("adj", ADJUDICATIONS, ids=lambda a: a.slug)
def test_decisive_verdicts_carry_a_valid_citation(adj):
    assert adj.evidence.strip()
    if adj.winner in _DECISIVE:  # detect/functional/neither_ii_v citam; modulating/ambiguous não
        assert isinstance(adj.citation, Citation)
        assert adj.citation.page >= 1
    else:
        assert adj.citation is None


@pytest.mark.parametrize("adj", ADJUDICATIONS, ids=lambda a: a.slug)
def test_identity_is_unique(adj):
    assert lookup_center_verdict(adj.slug) is adj


def test_decisive_verdict_without_citation_fails_fast():
    with pytest.raises(ValueError):
        TonalCenterVerdict(
            slug="x", curated_root="D", curated_mode="major",
            winner="functional", evidence="ii-V-I", citation=None,
        )


def test_winner_outside_enum_fails_fast():
    with pytest.raises(ValueError):
        TonalCenterVerdict(
            slug="x", curated_root="D", curated_mode="major",
            winner="relative", evidence="e", citation=_CIT,
        )


def test_invalid_mode_fails_fast():
    with pytest.raises(ValueError):
        TonalCenterVerdict(
            slug="x", curated_root="D", curated_mode="dorian",
            winner="detect", evidence="e", citation=_CIT,
        )


def test_verdict_without_evidence_fails_fast():
    with pytest.raises(ValueError):
        TonalCenterVerdict(
            slug="x", curated_root="D", curated_mode="major",
            winner="modulating", evidence="  ",
        )


def test_ambiguous_needs_no_citation():
    adj = TonalCenterVerdict(
        slug="embarcacao", curated_root="D#", curated_mode="major",
        winner="modulating", evidence="84 acordes; 2ª metade transposta ½t — sem tônica única.",
    )
    assert adj.winner == "modulating"
    assert adj.citation is None


def test_lookup_resolves_slug_variants():
    adj = TonalCenterVerdict(
        slug="Bolinha de Sabao", curated_root="C", curated_mode="major",
        winner="neither_ii_v", evidence="Dm7 G7 C7M = ii-V-I; nenhum pegou o I.",
        citation=_CIT,
    )
    assert adj.key == "bolinha-de-sabao"


def test_unknown_song_misses_cleanly():
    assert lookup_center_verdict("nao-existe") is None
