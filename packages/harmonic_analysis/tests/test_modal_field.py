"""Campo harmônico modal derivado, travado contra Chediak (pp. 122-125)."""

import pytest

from harmonic_analysis.domain.modal import CHARACTERISTIC_NOTE, modal_field

# Oráculo: (grau, qualidade) por modo, conforme as tabelas do Chediak.
CHEDIAK_FIELDS = {
    "ionian": [
        ("I", "maj7"), ("II", "m7"), ("III", "m7"), ("IV", "maj7"),
        ("V", "7"), ("VI", "m7"), ("VII", "m7b5"),
    ],
    "dorian": [
        ("I", "m7"), ("II", "m7"), ("bIII", "maj7"), ("IV", "7"),
        ("V", "m7"), ("VI", "m7b5"), ("bVII", "maj7"),
    ],
    "phrygian": [
        ("I", "m7"), ("bII", "maj7"), ("bIII", "7"), ("IV", "m7"),
        ("V", "m7b5"), ("bVI", "maj7"), ("bVII", "m7"),
    ],
    "lydian": [
        ("I", "maj7"), ("II", "7"), ("III", "m7"), ("#IV", "m7b5"),
        ("V", "maj7"), ("VI", "m7"), ("VII", "m7"),
    ],
    "mixolydian": [
        ("I", "7"), ("II", "m7"), ("III", "m7b5"), ("IV", "maj7"),
        ("V", "m7"), ("VI", "m7"), ("bVII", "maj7"),
    ],
    "aeolian": [
        ("I", "m7"), ("II", "m7b5"), ("bIII", "maj7"), ("IV", "m7"),
        ("V", "m7"), ("bVI", "maj7"), ("bVII", "7"),
    ],
    "locrian": [
        ("I", "m7b5"), ("bII", "maj7"), ("bIII", "m7"), ("IV", "m7"),
        ("bV", "maj7"), ("bVI", "7"), ("bVII", "m7"),
    ],
}


@pytest.mark.parametrize("mode,expected", CHEDIAK_FIELDS.items())
def test_modal_field_matches_chediak(mode, expected):
    assert modal_field("C", mode) == expected


def test_phrygian_seventh_degree_is_minor_not_dominant():
    field = dict(modal_field("E", "phrygian"))
    assert field["bVII"] == "m7"


def test_characteristic_notes():
    assert CHARACTERISTIC_NOTE["dorian"] == "6"
    assert CHARACTERISTIC_NOTE["phrygian"] == "b2"
    assert CHARACTERISTIC_NOTE["lydian"] == "#4"
    assert CHARACTERISTIC_NOTE["mixolydian"] == "b7"
    assert CHARACTERISTIC_NOTE["aeolian"] == "b6"
    assert CHARACTERISTIC_NOTE["locrian"] == "b2/b6"
