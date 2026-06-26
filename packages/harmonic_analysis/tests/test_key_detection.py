from harmonic_analysis.domain.key_detection import (
    detect_key,
    pitch_class_profile,
    segment_keys,
)

C_MAJOR = ["C", "F", "G", "C", "Am", "Dm", "G", "C"]
EB_MAJOR = ["Eb", "Ab", "Bb", "Eb", "Cm", "Fm", "Bb", "Eb"]


def test_profile_has_chord_tones_and_zeros():
    prof = pitch_class_profile(["C", "F", "G"])  # tons: C E G / F A C / G B D
    assert prof[0] > 0 and prof[4] > 0 and prof[7] > 0  # C, E, G presentes
    assert prof[1] == 0  # C# ausente de todos


def test_c_major_progression_detects_c_major():
    est = detect_key(C_MAJOR)
    assert est is not None
    assert est.name == "C major"


def test_detection_independent_of_first_chord():
    # mesma música resolvendo na tônica (C), começando em acordes diferentes
    a = detect_key(["C", "F", "Am", "Dm", "G", "C"])
    b = detect_key(["Am", "Dm", "G", "F", "C", "C"])
    assert (a.tonic_pc, a.mode) == (b.tonic_pc, b.mode) == (0, "major")


def test_result_carries_score_and_alternatives():
    est = detect_key(C_MAJOR)
    assert isinstance(est.score, float)
    assert len(est.alternatives) >= 1
    # a relativa menor (A minor) deve aparecer entre as melhores alternativas
    assert any("A minor" == name for name, _ in est.alternatives)


def test_single_key_piece_yields_one_region():
    regions = segment_keys(C_MAJOR)
    assert len(regions) == 1
    assert regions[0].estimate.name == "C major"


def test_modulation_yields_multiple_regions():
    regions = segment_keys(C_MAJOR + EB_MAJOR)
    assert len(regions) >= 2
    names = {r.estimate.name for r in regions}
    assert "C major" in names
    assert "Eb major" in names
