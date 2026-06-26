from harmonic_analysis.domain.key_detection import detect_key


def test_modal_piece_exposes_church_mode():
    est = detect_key(["G", "F", "C", "G"])
    assert est.church_mode == "mixolydian"


def test_tonal_piece_has_no_church_mode():
    est = detect_key(["C", "F", "G7", "C"])
    assert est.church_mode is None
    assert est.mode in ("major", "minor")
