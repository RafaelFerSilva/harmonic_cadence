"""Acordes de 7ª da dominante SEM função dominante (Chediak, pp. 111-113)."""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def fn(sym, nxt=None):
    return H.analyze_function(Chord(sym), None, Chord(nxt) if nxt else None)


def test_bVII7_is_minor_subdominant_not_secondary_dominant():
    code, name, _ = fn("Bb7", "C")
    assert code == "Emp"
    assert "bVII7" in name
    assert code != "Dsec"


def test_blues_sevenths_on_I_and_IV_are_not_secondary_dominants():
    i7, _, _ = fn("C7", "F7")
    iv7, _, _ = fn("F7", "Bb")
    assert i7 == "T"            # I7 blues, não V7/IV
    assert iv7 == "SD"          # IV7 blues, não V7/bVII


def test_vii7_resolving_to_tonic_is_cadential():
    code, name, _ = fn("B7", "C")
    assert code == "D"
    assert "cadencial" in name.lower()
    # no clichê IIIm: B7 -> Em resolve uma 5ª abaixo no III -> Dsec V7/III
    code2, name2, _ = fn("B7", "Em")
    assert code2 == "Dsec"
    assert "iii" in name2.lower()


def test_genuine_secondary_dominant_still_detected():
    code, name, _ = fn("E7", "Am")
    assert code == "Dsec"
    assert "vi" in name.lower()
