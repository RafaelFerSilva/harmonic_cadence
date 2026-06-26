"""Escala-acorde dos dominantes, ciente da qualidade (Chediak, pp. 113, 121)."""

from cifra_core.theory import Note, build_scale

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.chord_scale import recommended_scale
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def test_lydian_dominant_scale_built():
    scale = build_scale(Note.parse("C"), "lydian_dominant")
    assert [str(n) for n in scale] == ["C", "D", "E", "F#", "G", "A", "Bb"]


def test_blues_i7_maps_to_mixolydian_not_ionian():
    mode, _ = recommended_scale(Chord("C7"), H)
    assert mode == "mixolydian"


def test_bvii7_and_iv7_map_to_lydian_dominant():
    assert recommended_scale(Chord("Bb7"), H)[0] == "lydian_dominant"  # bVII7
    assert recommended_scale(Chord("F7"), H)[0] == "lydian_dominant"   # IV7


def test_diatonic_non_dominant_unchanged():
    assert recommended_scale(Chord("Cmaj7"), H)[0] == "ionian"
    assert recommended_scale(Chord("Dm7"), H)[0] == "dorian"
    assert recommended_scale(Chord("G7"), H)[0] == "mixolydian"  # V7
    assert recommended_scale(Chord("Dm7b5"), H)[0] == "locrian"
