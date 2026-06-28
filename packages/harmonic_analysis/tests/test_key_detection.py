from harmonic_analysis.domain.key_detection import (
    detect_key,
    dominant_regions,
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


# --- dominant_regions (pós-processamento) ----------------------------------

from harmonic_analysis.domain.key_detection import (  # noqa: E402
    KeyEstimate,
    KeyRegion,
)


def _region(start, end, tonic_pc, mode, score=0.9):
    name = f"{tonic_pc} {mode}"
    est = KeyEstimate(tonic_pc, mode, score, name, name)
    return KeyRegion(start, end, est)


def test_dominant_regions_single_region_passthrough():
    regions = [_region(0, 19, 0, "major")]
    out = dominant_regions(regions, 20)
    assert len(out) == 1
    assert (out[0].estimate.tonic_pc, out[0].estimate.mode) == (0, "major")


def test_dominant_regions_keeps_two_clear_tonal_areas():
    # Dm (10 acordes) seguido de D maior (10) — modulação tipo B (acorde pivô).
    regions = [_region(0, 9, 2, "minor"), _region(10, 19, 2, "major")]
    out = dominant_regions(regions, 20, min_pct=0.10)
    keys = {(r.estimate.tonic_pc, r.estimate.mode) for r in out}
    assert keys == {(2, "minor"), (2, "major")}


def test_dominant_regions_absorbs_tiny_fragment():
    # Fragmento de 1 acorde no meio de duas regiões de mesma tonalidade.
    regions = [
        _region(0, 8, 0, "major", score=0.90),
        _region(9, 9, 3, "major", score=0.50),   # minúsculo (1/20 < 10%)
        _region(10, 19, 0, "major", score=0.95),
    ]
    out = dominant_regions(regions, 20, min_pct=0.10)
    # absorvido e recoalescido: sobra uma única região de C (tonic 0)
    assert len(out) == 1
    assert (out[0].estimate.tonic_pc, out[0].estimate.mode) == (0, "major")
    assert (out[0].start, out[0].end) == (0, 19)


def test_dominant_regions_no_region_below_threshold():
    regions = [
        _region(0, 9, 0, "major"),
        _region(10, 10, 5, "major"),   # 1/12 < 10%
        _region(11, 11, 7, "minor"),   # 1/12 < 10%
    ]
    out = dominant_regions(regions, 12, min_pct=0.10)
    threshold = 0.10 * 12
    assert len(out) == 1 or all((r.end - r.start + 1) >= threshold for r in out)


def test_dominant_regions_does_not_modify_segment_keys():
    raw = segment_keys(C_MAJOR + EB_MAJOR)
    n = len(C_MAJOR + EB_MAJOR)
    out = dominant_regions(raw, n)
    # segment_keys segue intacto; dominant_regions só reduz/iguala a contagem
    assert len(out) <= len(raw)
    assert len(segment_keys(C_MAJOR + EB_MAJOR)) == len(raw)
