from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.voice_leading import (
    bass_motions,
    bass_note,
    descending_runs,
    line_cliches,
    pedal_points,
)


def chords(*syms):
    return [Chord(s) for s in syms]


def test_bass_uses_slash_note():
    assert bass_note(Chord("C/E")) == "E"
    assert bass_note(Chord("C")) == "C"


def test_bass_motion_stepwise_ascending():
    assert bass_motions(chords("C", "D")) == [2]


def test_chromatic_descending_bass():
    runs = descending_runs(chords("Dm", "Dm/C#", "Dm/C", "Dm/B"))
    assert len(runs) == 1
    assert runs[0]["chromatic"] is True


def test_diatonic_descending_bass():
    runs = descending_runs(chords("C", "G/B", "Am", "Am/G"))
    assert len(runs) == 1
    assert runs[0]["chromatic"] is False


def test_pedal_point_on_g():
    runs = pedal_points(chords("C/G", "F/G", "G", "C/G"))
    assert len(runs) == 1
    assert runs[0]["bass"] == "G"


def test_minor_line_cliche():
    runs = line_cliches(chords("Cm", "Cm(maj7)", "Cm7", "Cm6"))
    assert len(runs) == 1
    assert runs[0]["root"] == "C"
