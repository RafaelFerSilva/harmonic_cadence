"""Escalas dos dominantes alterados (Chediak P5, pp. 349-352)."""

from cifra_core.theory import Note, build_scale

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.chord_scale import recommended_scale
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def _pcs(mode):
    return {n.pitch_class for n in build_scale(Note.parse("C"), mode)}


def test_altered_scale_pitch_classes():
    assert _pcs("altered") == {0, 1, 3, 4, 6, 8, 10}
    assert _pcs("whole_tone") == {0, 2, 4, 6, 8, 10}
    assert _pcs("diminished") == {0, 1, 3, 4, 6, 7, 9, 10}


def test_flat_ninth_maps_to_diminished():
    assert recommended_scale(Chord("G7(b9)"), H)[0] == "diminished"


def test_sharp_ninth_maps_to_altered():
    assert recommended_scale(Chord("G7(#9)"), H)[0] == "altered"


def test_sharp_fifth_maps_to_whole_tone():
    assert recommended_scale(Chord("G7(#5)"), H)[0] == "whole_tone"


def test_flat_fifth_and_sharp_eleven_map_to_lydian_dominant():
    assert recommended_scale(Chord("G7(b5)"), H)[0] == "lydian_dominant"
    assert recommended_scale(Chord("G7(#11)"), H)[0] == "lydian_dominant"


def test_pm_dialect_matches_sharp_flat():
    assert recommended_scale(Chord("G7(9-)"), H)[0] == "diminished"  # 9- == b9
    assert recommended_scale(Chord("G7(5+)"), H)[0] == "whole_tone"  # 5+ == #5


def test_plain_dominant_unaltered():
    assert recommended_scale(Chord("G7"), H)[0] == "mixolydian"
    assert recommended_scale(Chord("Cmaj7"), H)[0] == "ionian"
