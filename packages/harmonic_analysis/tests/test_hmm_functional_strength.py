"""Emissão do HMM ponderada pela força funcional (Chediak, pág. 92)."""

from harmonic_analysis.domain.functional_hmm import parse_codes, parse_progression


def test_strong_function_is_more_confident_than_weak():
    parse = parse_progression(["C", "Am", "Dm", "G7"], key="C", mode="major")
    am = parse.chords[1]   # vi — fraco
    g7 = parse.chords[3]   # V  — forte
    assert g7.function == "D"
    assert g7.confidence > am.confidence


def test_weak_function_still_lists_alternatives():
    parse = parse_progression(["C", "Am", "Dm", "G7"], key="C", mode="major")
    am = parse.chords[1]
    assert 0.0 < am.confidence < 1.0
    assert len(am.alternatives) >= 1
    for _, p in am.alternatives:
        assert 0.0 < p < 1.0


def test_code_only_parse_uses_default_emission():
    syms = ["C", "F", "G7", "C"]
    a = parse_codes(["T", "SD", "D", "T"], syms).to_dict()
    b = parse_codes(["T", "SD", "D", "T"], syms, [None, None, None, None]).to_dict()
    assert a == b
    assert a["path"] == ["T", "SD", "D", "T"]


def test_weighted_parse_is_deterministic():
    a = parse_progression(["C", "Am", "Dm", "G7"], key="C").to_dict()
    b = parse_progression(["C", "Am", "Dm", "G7"], key="C").to_dict()
    assert a == b
