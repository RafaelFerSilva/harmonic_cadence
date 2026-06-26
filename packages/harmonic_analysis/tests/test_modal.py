from cifra_core.theory import root_pitch_class

from harmonic_analysis.domain.modal import (
    characteristic_degree,
    detect_mode,
    modal_cadences,
    modal_degree,
)


def test_mixolydian_detected_by_flat_seventh():
    info = detect_mode(["G", "F", "C", "G"])
    assert info is not None
    assert info.tonic == "G"
    assert info.mode == "mixolydian"


def test_dorian_detected_by_raised_sixth():
    info = detect_mode(["Dm", "G", "Em", "Dm"])  # resolve no "final" Dm
    assert info is not None
    assert info.tonic == "D"
    assert info.mode == "dorian"


def test_tonal_progression_is_not_modal():
    assert detect_mode(["C", "F", "G7", "C"]) is None


def test_bVII_is_a_modal_degree_not_chromatic():
    # F em G mixolídio é bVII (diatônico ao modo)
    f_pc = root_pitch_class("F")
    assert modal_degree(f_pc, "G", "mixolydian") == "bVII"


def test_characteristic_chord_of_dorian_is_IV():
    assert characteristic_degree("dorian") == "IV"
    g_pc = root_pitch_class("G")
    assert modal_degree(g_pc, "D", "dorian") == "IV"


def test_mixolydian_cadence_bVII_I():
    assert modal_cadences(["bVII", "I"], "mixolydian") == [("bVII", "I")]


def test_phrygian_cadence_bII_I():
    info = detect_mode(["Em", "F", "Em"])  # E frígio: F = bII
    assert info is not None and info.mode == "phrygian"
    f_pc = root_pitch_class("F")
    assert modal_degree(f_pc, "E", "phrygian") == "bII"
    assert modal_cadences(["bII", "I"], "phrygian") == [("bII", "I")]
