"""Gate de QUALIDADE: corrige o centro quando o K-S confunde o V com a tônica.

Discriminador funcional (Chediak): a tônica é repouso (maj7/6/m7/tríade); o V é tensão
(dominante-7). Se o centro do K-S aparece SÓ como dominante e resolve numa 5ª abaixo num
acorde de repouso, o K-S pegou o V. Guard do blues: sem repouso, aborta. As progressões
diatônicas e o desempate relativo (Fase B v1) NÃO podem regredir.
"""

from harmonic_analysis.domain.key_detection import (
    _i7_funk_anchor_path,
    _tritone_gate,
    detect_key,
)


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


# --- caminho B: ancorado por resolução (V-como-tônica que descansa às vezes) ---


def test_gate_path_b_corrects_v_that_rests_occasionally():
    # A Banda-like: Lá (Y) é predominante dominante mas descansa 1× (Lá tríade), então
    # o caminho A aborta. Ré (X=Y−7) é repouso predominante, Lá7→Ré resolve no fim, e
    # Ré é âncora (1º/último). O caminho B corrige Lá→Ré.
    syms = ["D", "A7", "D", "Bm", "A", "G", "A7", "D"]
    assert _tritone_gate(syms, (9, "major")) == (2, "major")


def test_gate_path_b_requires_structural_anchor():
    # Mesma resolução funcional e repouso predominante em Ré, mas Ré NÃO é o 1º nem o
    # último acorde (pontas em Mi menor) → o guard de âncora barra o caminho B.
    syms = ["Em", "A7", "D", "G", "D", "A", "A7", "D", "Em"]
    assert _tritone_gate(syms, (9, "major")) is None


def test_gate_path_b_requires_functional_dominant():
    # Ré é repouso predominante e âncora, mas nenhum V7/SubV funcional resolve nele
    # (Lá aparece só como tríade) → sem o crivo do trítono, o caminho B não dispara.
    assert _tritone_gate(["D", "A", "D", "Bm", "G", "D"], (9, "major")) is None


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


# --- âncora I7-funk (geometria INVERSA): K-S pega o IV de uma tônica funk I7 -------
# Chediak XXXIV. Recupera o centro quando a peça abre E fecha numa tônica I7 cujo IV
# o K-S elege. Sinal estrutural (first==last), não funcional. Ver i7-funk-anchor-gate.

# miniatura calibrada: K-S cru pega A maior (0.904), E é 2º (0.749); abre/fecha em E;
# E aparece como tríade (repouso) E como E7(9) (dominante I7); A = IV de E.
_FUNK = ["E", "E7(9)", "A7(13)", "E7(9)", "A7(13)", "A", "A", "A7(13)", "A",
         "C#m7", "A", "E"]


def test_i7_funk_anchor_corrects_iv_to_tonic():
    # K-S pega Lá (IV); o gate de âncora corrige p/ Mi (tônica funk I7).
    assert detect_key(_FUNK).name == "E major"


def test_i7_funk_helper_fires_on_funk_miniature():
    # ranked com Lá no topo, Mi em 2º — o helper devolve Mi (pc 4, maior).
    ranked = [(0.904, 9, "major"), (0.749, 4, "major"), (0.6, 1, "minor")]
    assert _i7_funk_anchor_path(_FUNK, (9, "major"), ranked) == (4, "major")


def test_i7_funk_does_not_fire_without_open_close_anchor():
    # Sem first==last (começa em A), guarda 1 falha → não dispara.
    seq = ["A", "E7(9)", "A7(13)", "E7(9)", "A7(13)", "A", "A", "E"]
    ranked = [(0.9, 9, "major"), (0.75, 4, "major")]
    assert _i7_funk_anchor_path(seq, (9, "major"), ranked) is None


def test_i7_funk_does_not_fire_on_pure_v_pedal():
    # X (E) só como dominante (E7), nunca tríade de repouso → guarda 4 falha (pedal de V).
    seq = ["E7", "A7(13)", "E7", "A7(13)", "A", "A", "E7"]
    ranked = [(0.9, 9, "major"), (0.75, 4, "major")]
    assert _i7_funk_anchor_path(seq, (9, "major"), ranked) is None


def test_i7_funk_does_not_fire_when_guess_is_not_iv():
    # Y não é o IV de X (X=E, Y=G≠A) → guarda 2 falha.
    seq = ["E", "E7", "A", "E"]
    ranked = [(0.9, 7, "major"), (0.7, 4, "major")]
    assert _i7_funk_anchor_path(seq, (7, "major"), ranked) is None


def test_i7_funk_does_not_touch_a_correct_diatonic_song():
    # ii-V-I em Dó: detecta Dó, o âncora não dispara (não abre/fecha igual + Y≠IV).
    assert detect_key(["Dm7", "G7", "Cmaj7", "Am7", "Dm7", "G7", "Cmaj7"]).name == "C major"
