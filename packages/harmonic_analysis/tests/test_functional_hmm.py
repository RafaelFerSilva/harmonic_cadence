"""Camada 3 — parsing funcional probabilístico (HMM + Viterbi)."""

from harmonic_analysis.domain.functional_hmm import (
    STATES,
    parse_codes,
    parse_progression,
    transition_prob,
)


def test_clear_cycle_yields_expected_path():
    # C F G7 C → T SD D T
    parse = parse_progression(["C", "F", "G7", "C"], key="C", mode="major")
    assert parse.path == ["T", "SD", "D", "T"]


def test_dominant_to_tonic_is_a_likely_transition():
    # D→T é a transição mais forte saindo da dominante (gramática funcional).
    assert transition_prob("D", "T") == max(transition_prob("D", s) for s in STATES)


def test_unambiguous_dominant_has_high_confidence():
    parse = parse_progression(["C", "F", "G7", "C"], key="C", mode="major")
    g7 = parse.chords[2]
    assert g7.function == "D"
    assert g7.confidence > 0.8
    # confiança da escolhida domina qualquer alternativa
    assert all(g7.confidence > p for _, p in g7.alternatives)


def test_ambiguous_chord_lists_alternatives():
    # vi (Am) é lido como tônica, mas admite leitura predominante → alternativas.
    parse = parse_progression(["C", "Am", "Dm", "G7"], key="C", mode="major")
    am = parse.chords[1]
    assert am.confidence < parse.chords[2].confidence  # menos confiante que G7→? Dm
    assert len(am.alternatives) >= 1
    for _, prob in am.alternatives:
        assert 0.0 < prob < 1.0


def test_parse_is_deterministic():
    a = parse_progression(["C", "F", "G7", "C"], key="C").to_dict()
    b = parse_progression(["C", "F", "G7", "C"], key="C").to_dict()
    assert a == b


def test_parse_codes_bridges_function_codes():
    parse = parse_codes(["T", "SD", "D", "T"], ["C", "F", "G7", "C"])
    assert parse.path == ["T", "SD", "D", "T"]
    assert parse.chords[0].label == "T"
