from cifra_core.theory import (
    Note,
    build_scale,
    interval_magnitude,
    interval_semitones,
    realize,
)


# --- Note / spelling ----------------------------------------------------------

def test_enharmonic_distinct_same_pitch_class():
    db, cs = Note.parse("Db"), Note.parse("C#")
    assert db != cs
    assert db.pitch_class == cs.pitch_class == 1


def test_letter_and_accidental_recoverable():
    n = Note.parse("Bb")
    assert n.letter == "B"
    assert n.accidental == -1
    assert str(n) == "Bb"


# --- intervals ----------------------------------------------------------------

def test_ascending_fourth_is_five_semitones():
    assert interval_semitones(Note.parse("E"), Note.parse("A")) == 5


def test_tritone_magnitude_is_six():
    assert interval_magnitude(Note.parse("C"), Note.parse("F#")) == 6


# --- chord realization --------------------------------------------------------

def _pcs(*names):
    return frozenset(Note.parse(n).pitch_class for n in names)


def test_major_seventh_realizes_to_four_tones():
    assert realize("Cmaj7") == _pcs("C", "E", "G", "B")


def test_half_diminished_realizes_correctly():
    assert realize("Dm7b5") == _pcs("D", "F", "Ab", "C")


def test_brazilian_7M_equals_maj7():
    assert realize("C7M") == realize("Cmaj7")


# --- scales / modes -----------------------------------------------------------

def test_mixolydian_has_flat_seventh():
    scale = build_scale(Note.parse("G"), "mixolydian")
    assert Note("F", 0) in scale  # F natural, não F#


def test_major_scale_one_letter_per_degree_with_flat_spelling():
    scale = build_scale(Note.parse("F"), "major")
    assert str(scale[3]) == "Bb"  # 4º grau
    assert sorted(n.letter for n in scale) == list("ABCDEFG")
