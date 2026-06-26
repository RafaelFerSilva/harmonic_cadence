from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.chord_scale import analyze_chord, recommended_scale
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def test_tonic_major_maps_to_ionian():
    mode, _ = recommended_scale(Chord("Cmaj7"), H)
    assert mode == "ionian"


def test_ii_maps_to_dorian():
    mode, _ = recommended_scale(Chord("Dm7"), H)
    assert mode == "dorian"


def test_dominant_maps_to_mixolydian():
    mode, _ = recommended_scale(Chord("G7"), H)
    assert mode == "mixolydian"


def test_half_diminished_maps_to_locrian():
    mode, _ = recommended_scale(Chord("Dm7b5"), H)
    assert mode == "locrian"


def test_imaj7_tensions_and_avoid_natural_11():
    info = analyze_chord(Chord("Cmaj7"), H)
    assert set(info["tensions"]) == {"9", "13"}
    assert "11" in info["avoid"]


def test_iim7_dorian_makes_11_available():
    info = analyze_chord(Chord("Dm7"), H)
    assert set(info["tensions"]) == {"9", "11", "13"}
    assert info["avoid"] == []
