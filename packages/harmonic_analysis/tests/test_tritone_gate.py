"""Gate de QUALIDADE: corrige o centro quando o K-S confunde o V com a tônica.

Discriminador funcional (Chediak): a tônica é repouso (maj7/6/m7/tríade); o V é tensão
(dominante-7). Se o centro do K-S aparece SÓ como dominante e resolve numa 5ª abaixo num
acorde de repouso, o K-S pegou o V. Guard do blues: sem repouso, aborta. As progressões
diatônicas e o desempate relativo (Fase B v1) NÃO podem regredir.
"""

from harmonic_analysis.domain.key_detection import _tritone_gate, detect_key


# --- o gate de qualidade ------------------------------------------------------


def test_gate_corrects_v_detected_as_tonic():
    # Garota em miniatura: Dó aparece SÓ como Dó7, resolve em Fá (Fámaj7 = repouso).
    # K-S "acha" Dó (o V). O gate corrige p/ Fá.
    syms = ["Fmaj7", "G7", "Gm7", "C7", "Fmaj7"]
    assert _tritone_gate(syms, (0, "major")) == (5, "major")


def test_gate_does_not_touch_a_resting_tonic():
    # Dó aparece como Dó (repouso, tríade) → o K-S está certo → sem override.
    assert _tritone_gate(["C", "F", "G7", "C"], (0, "major")) is None


def test_gate_blues_tonic_is_not_demoted():
    # Blues em Dó: Dó7 → Fá7 → Sol7. O alvo Fá aparece como Fá7 (NÃO é repouso) →
    # gate ABORTA → Dó7 segue como tônica (mixolídio/blues, não V funcional).
    assert _tritone_gate(["C7", "F7", "C7", "G7", "F7", "C7"], (0, "major")) is None


def test_gate_aborts_when_dominant_does_not_resolve():
    # Dó7 nunca resolve numa 5ª abaixo (Fá) → guard → sem override.
    assert _tritone_gate(["C7", "Bb", "C7", "Bb"], (0, "major")) is None


def test_gate_returns_none_when_ks_center_absent():
    # O centro do K-S não aparece como raiz de acorde → nada a julgar.
    assert _tritone_gate(["Dm7", "G7", "Em7", "A7"], (0, "major")) is None


# --- não-regressão (a invariante das 41 / diatônico) --------------------------


def test_diatonic_major_unchanged():
    est = detect_key(["C", "F", "G", "C", "Am", "Dm", "G", "C"])
    assert (est.tonic_pc, est.mode) == (0, "major")


def test_relative_minor_still_resolves_by_cadence():
    est = detect_key(["C", "Am", "Dm", "E7", "Am"])
    assert est.mode == "minor" and est.tonic_pc == 9


def test_clear_major_cadence_is_c():
    est = detect_key(["C", "F", "G7", "C"])
    assert (est.tonic_pc, est.mode) == (0, "major")


def test_tonic_appearing_as_maj7_is_kept():
    # Mesmo havendo G7→C, Dó aparece como Cmaj7 (repouso) → não vira "V de Fá".
    est = detect_key(["Cmaj7", "Am7", "Dm7", "G7", "Cmaj7"])
    assert (est.tonic_pc, est.mode) == (0, "major")
