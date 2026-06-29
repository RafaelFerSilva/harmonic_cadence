"""Invariante do corpus de centros modais — o gate que torna a citação obrigatória.

A obrigação real é o `make test`: nenhum fato modal pode existir sem uma `Citation`
válida, e construir um `ModalCenterFact` sem citação levanta `TypeError` na
importação. Defesa em profundidade sobre o `__post_init__` (runtime) + `Literal`
(IDE/mypy).
"""

import pytest

from harmonic_analysis.corpus.modal_centers import (
    CORPUS,
    Citation,
    ModalCenterFact,
    lookup_modal_center,
)


@pytest.mark.parametrize("fact", CORPUS, ids=lambda f: f.song)
def test_every_fact_has_a_valid_citation(fact):
    assert isinstance(fact.citation, Citation)
    assert fact.citation.source.strip()
    assert fact.citation.volume >= 1
    assert fact.citation.page >= 1


@pytest.mark.parametrize("fact", CORPUS, ids=lambda f: f.song)
def test_every_fact_has_a_curated_finalis_offset(fact):
    # Divergência de centro real (D4): offset ≠ 0 (senão é nome-de-modo só, parte A).
    assert fact.finalis_from_tonal != 0
    assert 0 <= fact.finalis_from_tonal < 12


def test_citation_cannot_be_omitted():
    with pytest.raises(TypeError):  # sem citation → não constrói (kw_only, sem default)
        ModalCenterFact(
            artist="x",
            song="y",
            curated_center="A",
            curated_mode="dorian",
            finalis_from_tonal=7,
        )


def test_empty_citation_source_fails_fast():
    with pytest.raises(ValueError):
        Citation(source="  ", volume=1, page=125)


def test_invalid_page_fails_fast():
    with pytest.raises(ValueError):
        Citation(source="Almir Chediak", volume=1, page=0)


def test_finalis_offset_out_of_range_fails_fast():
    with pytest.raises(ValueError):
        ModalCenterFact(
            artist="x",
            song="y",
            curated_center="A",
            curated_mode="dorian",
            finalis_from_tonal=12,
            citation=Citation(source="Almir Chediak", volume=1, page=1),
        )


def test_arrastao_is_in_the_corpus():
    fact = lookup_modal_center("Edu Lobo", "Arrastao")
    assert fact is not None
    assert fact.curated_center == "A"
    assert fact.curated_mode == "dorian"
    assert fact.citation.page == 125


@pytest.mark.parametrize(
    "artist,song",
    [
        ("Edu Lobo", "Arrastao"),
        ("Edu Lobo", "Arrastão"),  # acento resolve via slug
        ("edu lobo", "arrastao"),  # caixa variante resolve
        ("EDU LOBO", "ARRASTÃO"),
    ],
)
def test_identity_matching_resolves_variants(artist, song):
    fact = lookup_modal_center(artist, song)
    assert fact is not None
    assert fact.song == "Arrastao"


def test_excluded_mode_name_only_songs_miss():
    # Upa Neguinho / Pra Não Dizer: centro já correto → parte (A), fora do CORPUS (D4).
    assert lookup_modal_center("Edu Lobo", "Upa Neguinho") is None
    assert (
        lookup_modal_center("Geraldo Vandre", "Pra Nao Dizer Que Nao Falei das Flores")
        is None
    )


def test_unknown_song_misses_cleanly():
    assert lookup_modal_center("Tom Jobim", "Garota de Ipanema") is None
