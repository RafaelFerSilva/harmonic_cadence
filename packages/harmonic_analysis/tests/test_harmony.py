from harmonic_analysis.domain.cadence import analyze_cadences
from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis


def test_chord_to_degree():
    analysis = HarmonicAnalysis("C", "major")
    assert analysis.get_degree(Chord("C")) == "I"
    assert analysis.get_degree(Chord("G")) == "V"


def test_authentic_cadence_detected():
    cad = analyze_cadences(["V", "I"], "major", ["G", "C"])
    assert "G → C" in cad["Perfeita"]  # V→I em estado fundamental (Chediak)
