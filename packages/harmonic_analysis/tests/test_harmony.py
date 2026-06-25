from domain.chord import Chord
from domain.harmony import HarmonicAnalysis


def test_chord_to_degree():
    chord = Chord("C")
    analysis = HarmonicAnalysis("C", "major")
    assert analysis.get_degree(chord) == "I"


def test_detect_cadence():
    from domain.cadence import detect_cadences

    seq = ["ii", "V", "I"]
    cad = detect_cadences(seq)
    assert ("Autêntica", 1) in cad
