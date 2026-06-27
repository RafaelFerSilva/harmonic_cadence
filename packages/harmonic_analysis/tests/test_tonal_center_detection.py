"""Fase B v1: desempate cadencial sobre o K-S (tonal-center-detection).

A confusão maior↔relativa-menor é um quase-empate estrutural (mesma coleção
diatônica). O estágio de corroboração usa sinais funcionais que o histograma
descarta — 1º acorde, último acorde+qualidade, cadência autêntica dominante→tônica
— para decidir na banda de empate, sem sobrepor um K-S confiante.
"""

from harmonic_analysis.domain.key_detection import (
    CORROB_CADENCE,
    cadence_corroboration,
    detect_key,
)

# C maior = pc 0; A menor = pc 9; D menor = pc 2.


def test_corroboration_favors_major_on_authentic_major_cadence():
    """Termina G7→C: corrobora Dó maior mais que Lá menor."""
    syms = ["Am", "Em", "F", "Am", "Dm", "Em", "G7", "C"]
    assert cadence_corroboration(syms, 0, "major") > cadence_corroboration(syms, 9, "minor")


def test_corroboration_favors_minor_on_authentic_minor_cadence():
    """Termina E7→Am: corrobora Lá menor mais que Dó maior."""
    syms = ["Am", "G", "F", "E7", "Am"]
    assert cadence_corroboration(syms, 9, "minor") > cadence_corroboration(syms, 0, "major")


def test_subv_tritone_resolution_counts_as_cadence():
    """Db7→C é SubV→I (substituto tritonal): cadência autêntica em MPB/bossa,
    deve contar o bônus de cadência para Dó maior."""
    with_subv = cadence_corroboration(["Dm", "Db7", "C"], 0, "major")
    without = cadence_corroboration(["Dm", "F", "C"], 0, "major")  # sem resolução
    assert with_subv - without >= CORROB_CADENCE


def test_bass_pedal_is_the_tonal_anchor_not_the_root():
    """A Sina termina em D/A (Ré sobre pedal de Lá): o baixo Lá ancora o tom,
    então a corroboração favorece Lá, não Ré."""
    sina = ["A", "D/A", "A", "F#m7", "C#7", "D7M", "A", "D/A"]
    assert cadence_corroboration(sina, 9, "major") > cadence_corroboration(sina, 2, "major")


def test_relative_near_tie_flips_to_major_by_cadence():
    """K-S lê Lá menor (0.875) com Dó maior em quase-empate (0.845); a cadência
    autêntica G7→C deve virar para Dó maior."""
    est = detect_key(["Am", "Em", "F", "Am", "Dm", "Em", "G7", "C"])
    assert est.name == "C major"


def test_true_minor_stays_minor():
    """Cadência E7→Am corrobora a menor real — não deve virar maior."""
    est = detect_key(["Am", "G", "F", "E7", "Am"])
    assert est.name == "A minor"


def test_confident_ks_is_not_overridden():
    """Dó maior claro (fora da banda de empate) permanece intocado."""
    est = detect_key(["C", "F", "G", "C", "Am", "Dm", "G", "C"])
    assert est.name == "C major"


def test_estimate_shape_preserved():
    """O contrato do KeyEstimate (campos e alternativas) é mantido."""
    est = detect_key(["Am", "Em", "F", "Am", "Dm", "Em", "G7", "C"])
    assert est.key_note and est.mode in ("major", "minor")
    assert isinstance(est.score, float)
    assert len(est.alternatives) >= 1
    # a chave escolhida não se repete nas alternativas
    assert all(alt[0] != est.name for alt in est.alternatives)
