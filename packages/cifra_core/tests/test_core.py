import dataclasses

import pytest

from cifra_core import (
    ChordPattern,
    Cifra,
    SongRef,
    clean_cifra_lines,
    fix_encoding,
    slugify,
)


# --- fix_encoding -------------------------------------------------------------

def test_fix_encoding_repairs_mojibake():
    assert fix_encoding("jÃ¡ nÃ£o") == "já não"


def test_fix_encoding_passthrough_for_correct_text():
    assert fix_encoding("já não") == "já não"


def test_fix_encoding_returns_undecodable_untouched():
    # caractere fora de latin1 não pode ser re-decodificado → devolvido intacto
    assert fix_encoding("日本") == "日本"


# --- slugify ------------------------------------------------------------------

def test_slugify_strips_accents_and_hyphenates():
    assert slugify("João Gilberto") == "joao-gilberto"


def test_slugify_normalizes_case_and_punctuation():
    assert slugify("Garota de Ipanema!") == "garota-de-ipanema"


def test_slugify_is_deterministic():
    assert slugify("Tom Jobim") == slugify("Tom Jobim")


# --- chord regex --------------------------------------------------------------

def _chords(text):
    return [c for c in ChordPattern.find_all(text) if c]


def test_chord_regex_matches_simple_and_complex():
    assert _chords("C  Am7  G/B  F#m7b5  Bb7(9)  E7M(9)") == [
        "C",
        "Am7",
        "G/B",
        "F#m7b5",
        "Bb7(9)",
        "E7M(9)",
    ]


def test_chord_regex_ignores_plain_words():
    assert _chords("vem comigo meu amor") == []


# --- line filter --------------------------------------------------------------

RAW = [
    "[Intro]",
    "tom: C",
    "Parte 1 de 2",
    "E|---0---2---",
    "C      Am",
    "Vem comigo",
    "C      Am",
    "",
    "G  F",
]
EXPECTED = ["C      Am", "Vem comigo", "C      Am", "G  F"]


def test_filter_removes_tab_and_markers_keeps_chords_and_lyrics_in_order():
    assert clean_cifra_lines(RAW) == EXPECTED


def test_filter_is_idempotent():
    once = clean_cifra_lines(RAW)
    assert clean_cifra_lines(once) == once


def test_filter_collapses_consecutive_duplicates():
    assert clean_cifra_lines(["C  G", "C  G", "C  G", "Am"]) == ["C  G", "Am"]


# --- models -------------------------------------------------------------------

def test_cifra_round_trips_through_serialization():
    c = Cifra(
        artist="Djavan",
        name="Sina",
        cifra=("C  Am", "G  F"),
        cifra_html="<b>x</b>",
        youtube_url="yt",
        cifraclub_url="cc",
    )
    assert Cifra.from_api(c.to_dict()) == c


def test_cifra_is_empty_reflects_chart_lines():
    assert Cifra(artist="a", name="b").is_empty is True
    assert Cifra(artist="a", name="b", cifra=("C",)).is_empty is False


def test_cifra_is_immutable():
    c = Cifra(artist="a", name="b")
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.artist = "x"  # type: ignore[misc]


def test_songref_carries_listing_metadata():
    sr = SongRef.from_api(
        {"name": "Sina", "slug": "sina", "url": "u", "only_lyrics": False}
    )
    assert (sr.name, sr.slug, sr.url, sr.only_lyrics) == ("Sina", "sina", "u", False)
