"""Correção de modo paralelo (parallel-mode-correction).

A confusão paralela (mesma tônica, maior↔menor) não é distinguida pela cadência
(a dominante é comum) nem pelo histograma K-S; o sinal é a QUALIDADE dos acordes
de tônica, e a correção só age na tônica em que a peça assenta (gate de âncora-baixo).
"""

from harmonic_analysis.domain.key_detection import (
    _correct_parallel_mode,
    detect_key,
)

# Dó = pc 0.


def test_major_read_corrected_to_minor_when_tonic_chords_are_minor():
    # Assenta em Dó (G7→Cm, termina em Cm) e os acordes de tônica são menores.
    assert _correct_parallel_mode(["Cm", "Fm", "G7", "Cm"], 0, "major") == "minor"


def test_minor_read_corrected_to_major_when_tonic_chords_are_major():
    assert _correct_parallel_mode(["C", "F", "G7", "C"], 0, "minor") == "major"


def test_cadence_anchor_allows_correction_even_if_last_chord_is_not_tonic():
    # Termina em Eb, mas há cadência G7→Cm → âncora em Dó; corrige p/ menor.
    assert _correct_parallel_mode(["Cm", "Fm", "G7", "Cm", "Eb"], 0, "major") == "minor"


def test_gate_blocks_correction_on_non_anchored_tonic():
    # Há acordes de Dó menor, MAS a peça cadência/assenta em Lá (não em Dó) →
    # Dó não é âncora → não inverte (protege a confusão relativa).
    assert _correct_parallel_mode(["Cm", "Cm", "Dm", "E7", "Am"], 0, "major") == "major"


def test_isolated_minor_borrowing_does_not_flip_major():
    # Maior com um único `i` de passagem: voto fraco (−1) < limiar → fica maior.
    assert _correct_parallel_mode(["C", "Cm", "F", "G7", "C"], 0, "major") == "major"


def test_sina_stays_a_major_no_false_parallel_flip():
    # A Sina é Lá maior (acordes de tônica maiores) — o voto não dispara menor.
    sina = ["A", "D/A", "A", "F#m7", "C#7", "D7M", "A", "D/A"]
    est = detect_key(sina)
    assert est.name == "A major"
