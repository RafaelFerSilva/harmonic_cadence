"""Camada 3 — impressão digital de estilo."""

from harmonic_analysis.domain.style_fingerprint import (
    build_fingerprint,
    compare,
    distance,
    similarity,
)
from harmonic_analysis.services.analysis_service import AnalysisService


def _analyze(cifra_lines):
    """Análise offline (sem provider) de uma cifra dada como lista de linhas."""
    return AnalysisService(None).analyze_song_data_structured(
        {"name": "x", "artist": "y", "cifra": cifra_lines}
    )


# Corpus "pop diatônico": cadências simples I–IV–V–I.
POP = [
    _analyze(["C F G C", "C G Am F"]),
    _analyze(["G C D G", "G D Em C"]),
]

# Corpus "jazz cromático": dominantes secundários, trítono-subs, ii-V.
JAZZ = [
    _analyze(["Cmaj7 A7 Dm7 G7", "Em7 A7 Dm7 Db7 Cmaj7"]),
    _analyze(["Dm7 G7 Cmaj7 E7", "Am7 D7 Dm7 G7 Cmaj7"]),
]


def test_function_distribution_is_a_normalized_profile():
    fp = build_fingerprint(POP)
    weights = fp.function_distribution
    assert abs(sum(weights.values()) - 1.0) < 1e-9
    for w in weights.values():
        assert w > 0.0  # toda função presente tem peso não-nulo


def test_fingerprint_has_expected_sections():
    fp = build_fingerprint(JAZZ).to_dict()
    for key in (
        "function_distribution",
        "transition_matrix",
        "cadence_counts",
        "modal_usage",
        "tension_density",
    ):
        assert key in fp


def test_identical_corpora_are_maximally_similar():
    fp = build_fingerprint(POP)
    assert abs(similarity(fp, fp) - 1.0) < 1e-9
    assert abs(distance(fp, fp)) < 1e-9


def test_different_corpora_differ():
    pop = build_fingerprint(POP)
    jazz = build_fingerprint(JAZZ)
    self_sim = similarity(pop, pop)
    cross_sim = similarity(pop, jazz)
    assert cross_sim < self_sim
    summary = compare(pop, jazz)
    assert summary["distance"] > 0.0
