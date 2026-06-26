"""Capability harmonic-function (Chediak, pp. 91-96)."""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmonic_function import (
    FUNCTION_BY_DEGREE,
    functional_strength,
    is_diatonic_minor,
    minor_function,
    tonal_function,
)
from harmonic_analysis.domain.harmony import HarmonicAnalysis


# --- R1: classificação diatônica de função (pág. 96) --------------------------

def test_major_tonic_degrees():
    assert tonal_function("I") == "T"
    assert tonal_function("iii") == "T"
    assert tonal_function("vi") == "T"


def test_major_subdominant_degrees():
    assert tonal_function("IV") == "SD"
    assert tonal_function("ii") == "SD"


def test_major_dominant_degrees():
    assert tonal_function("V") == "D"
    assert tonal_function("vii°") == "D"


def test_function_via_chord_degree_in_c_major():
    h = HarmonicAnalysis("C", "major")
    fn = lambda s: tonal_function(h.get_degree(Chord(s)))  # noqa: E731
    assert [fn(s) for s in ["C", "Em", "Am"]] == ["T", "T", "T"]
    assert [fn(s) for s in ["F", "Dm"]] == ["SD", "SD"]
    assert [fn(s) for s in ["G7", "Bm7b5"]] == ["D", "D"]


# --- R2: qualidade funcional (pág. 92) ----------------------------------------

def test_principal_degrees_are_strong():
    assert [functional_strength(d) for d in ["I", "IV", "V"]] == ["strong"] * 3


def test_substitutes_of_sd_and_d_are_medium():
    assert [functional_strength(d) for d in ["II", "VII"]] == ["medium"] * 2


def test_substitutes_of_tonic_are_weak():
    assert [functional_strength(d) for d in ["III", "VI"]] == ["weak"] * 2


def test_strength_consistent_with_function_table():
    # todo grau classificado por função tem também uma força definida
    assert set(FUNCTION_BY_DEGREE) == {"I", "II", "III", "IV", "V", "VI", "VII"}


# --- R3: campo menor sobre três escalas (pp. 94-96) ---------------------------

def test_chord_diatonic_to_any_minor_scale():
    assert is_diatonic_minor("G7", "C")    # V7 (harmônica/melódica)
    assert is_diatonic_minor("Gm7", "C")   # Vm7 (natural)
    assert is_diatonic_minor("Bb7", "C")   # bVII7 (natural)


def test_natural_minor_five_has_no_dominant_function():
    assert minor_function("Gm7", "C") != "D"
    assert minor_function("Gm7", "C") is None


def test_minor_tonic_family():
    assert minor_function("Cm7", "C") == "T"
    assert minor_function("Cm7M", "C") == "T"
