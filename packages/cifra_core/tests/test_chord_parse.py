"""Bateria de parsing de acorde ancorada no corpus e no Chediak.

Oráculo: conjunto de classes de altura esperado (verdade de teoria) para os
acordes reais mais comuns do corpus + os cenários das specs `chord-parsing`.
"""

import pytest

from cifra_core.theory import Category, Fifth, Seventh, Third, parse, realize


def _pcs(*names):
    from cifra_core.theory import Note
    return frozenset(Note.parse(n).pitch_class for n in names)


# --- Bateria do corpus (Cifra Club / dialeto ±) -------------------------------

CORPUS_BATTERY = {
    "A7(13-)": ("A", "C#", "E", "G", "F"),       # b13 = F (não F#)
    "Em7(5-)": ("E", "G", "Bb", "D"),            # meio-diminuto
    "Db7(5+/9+)": ("Db", "F", "A", "B", "E"),    # #5, #9
    "G7M": ("G", "B", "D", "F#"),
    "C7M(5+)": ("C", "E", "G#", "B"),
    "D7(9/11+)": ("D", "F#", "A", "C", "E", "G#"),
    "A7(9-/13)": ("A", "C#", "E", "G", "Bb", "F#"),
    "C6/9": ("C", "E", "G", "A", "D"),
    "A7(4)": ("A", "D", "E", "G"),               # 7sus4
    "B2": ("B", "D#", "F#", "C#"),               # add9, terça mantida
    "D#°": ("D#", "F#", "A", "C"),               # dim7
    "G7(9/13)": ("G", "B", "D", "F", "A", "E"),
}


@pytest.mark.parametrize("symbol,notes", CORPUS_BATTERY.items())
def test_corpus_battery_realizes_correctly(symbol, notes):
    assert realize(symbol) == _pcs(*notes)


# --- Cenários das specs (music-theory-core) -----------------------------------

def test_bare_diminished_is_diminished_seventh():
    assert realize("C°") == _pcs("C", "Eb", "Gb", "A")
    assert realize("C°") == realize("Cdim7")


def test_suspended_chords_omit_the_third():
    assert realize("Csus4") == _pcs("C", "F", "G")
    assert realize("C4") == _pcs("C", "F", "G")
    assert realize("Csus2") == _pcs("C", "D", "G")


def test_altered_ninth_not_double_counted():
    pcs = realize("C7(#9)")
    assert _pcs("D#") <= pcs        # tem a #9
    assert _pcs("D").isdisjoint(pcs)  # não tem a 9 natural


def test_bare_odd_extension_implies_seventh():
    assert _pcs("F") <= realize("G9")    # 7ª da dominante presente
    assert _pcs("F") <= realize("G13")
    assert _pcs("Bb").isdisjoint(realize("Cadd9"))  # add9 sem 7ª
    assert realize("Cadd9") == _pcs("C", "E", "G", "D")


def test_slash_bass_joins_realized_set():
    assert _pcs("Bb") <= realize("C/Bb")
    assert realize("C/Bb") == _pcs("C", "E", "G", "Bb")


# --- Dialetos (± ≡ #/b) -------------------------------------------------------

def test_plus_minus_equals_sharp_flat():
    assert realize("C7(9-)") == realize("C7(b9)")
    assert realize("C7(5+)") == realize("C7(#5)")
    assert realize("A7(13-)") == realize("A7(b13)")


def test_flat_second_is_flat_ninth():
    assert realize("A7(2-/13-)") == realize("A7(b9/b13)")


# --- Slots / ParsedChord ------------------------------------------------------

def test_altered_fifth_and_tension_are_distinct():
    p = parse("C7(#11)")
    assert p.fifth is Fifth.PERFECT
    assert 6 in p.tensions          # #11
    assert {6, 7} <= p.pitch_classes() ^ {0}  # 6 e 7 distintos (a partir da raiz C)


def test_suspension_in_third_slot():
    p = parse("G7sus4")
    assert p.third is Third.SUS4
    assert p.seventh is Seventh.MINOR
    assert p.category() is Category.SUSPENDED


def test_added_vs_extension():
    assert parse("C6").seventh is Seventh.NONE
    assert parse("C9").seventh is Seventh.MINOR


def test_category_from_slots():
    assert parse("G7").category() is Category.DOMINANT     # 3M + 7m
    assert parse("G9").category() is Category.DOMINANT
    assert parse("C").category() is Category.MAJOR
    assert parse("Cm7").category() is Category.MINOR
    assert parse("Bdim7").category() is Category.DIMINISHED
    assert parse("Em7b5").category() is Category.HALF_DIMINISHED


def test_bass_independent_of_membership():
    assert str(parse("C/Bb").bass) == "Bb"
    assert str(parse("C/G").bass) == "G"


# --- Extração (ChordPattern) --------------------------------------------------

def test_extraction_pm_alterations_and_power_and_slash_tone():
    from cifra_core import ChordPattern

    def chords(text):
        return [c for c in ChordPattern.find_all(text) if c]

    assert chords("A7(13-)  Db7(5+/9+)  Em7(5-)") == [
        "A7(13-)", "Db7(5+/9+)", "Em7(5-)",
    ]
    assert chords("C5  G5") == ["C5", "G5"]          # power chords não truncam
    assert chords("C6/9  Am7") == ["C6/9", "Am7"]    # /9 é tom, não baixo
    assert chords("C/Bb  D/A") == ["C/Bb", "D/A"]    # baixo invertido
