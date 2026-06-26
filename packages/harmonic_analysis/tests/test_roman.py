from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def rn(sym, nxt=None):
    return H.roman_numeral(Chord(sym), Chord(nxt) if nxt else None)


def test_diatonic_triads_with_quality():
    got = [rn(s) for s in ["C", "Dm", "Em", "F", "G", "Am", "Bdim"]]
    assert got == ["I", "ii", "iii", "IV", "V", "vi", "vii°"]


def test_seventh_quality_reflected():
    assert rn("G7") == "V7"
    assert rn("Cmaj7") == "Imaj7"


def test_first_inversion_triad():
    assert rn("C/E") == "I6"


def test_second_inversion_triad():
    assert rn("C/G") == "I6/4"


def test_seventh_first_inversion():
    assert rn("G7/B") == "V6/5"


def test_root_position_has_no_figure():
    assert rn("G7") == "V7"


def test_applied_dominant_numeral():
    assert rn("E7", "Am") == "V7/vi"
