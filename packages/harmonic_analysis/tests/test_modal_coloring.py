"""Coloração modal: overlay aditivo, ancorado, assimétrico (mixolídio/frígio).

Testes determinísticos com progressões sintéticas por modo. A regra é calibrada
contra o ground-truth de Chediak (ver scripts/modal_coloring_groundtruth.py).
"""

from harmonic_analysis.domain.modal_coloring import detect_coloring


# --- 4.1 gatilho dispara onde deve --------------------------------------------


def test_mixolydian_from_bVII_to_I_cadence_major():
    # G maior com F (bVII) → G (I): cadência mixolídia.
    c = detect_coloring("G", "major", ["G", "F", "G", "C", "F", "G"])
    assert c is not None and c["flavor"] == "mixolydian"
    assert any("bVII→I" in e for e in c["evidence"])


def test_mixolydian_from_recurrent_minor_v_major():
    # D maior com Am (v menor) recorrente, SEM bVII (estilo Upa Neguinho).
    c = detect_coloring("D", "major", ["D", "Am", "D", "G", "Am", "D"])
    assert c is not None and c["flavor"] == "mixolydian"
    assert any("v menor" in e for e in c["evidence"])


def test_phrygian_from_structural_bII_to_i_minor():
    # D menor com Eb (bII) → Dm (i) repetido: cadência frígia estrutural.
    c = detect_coloring("D", "minor", ["Dm", "Eb", "Dm", "Eb", "Dm"])
    assert c is not None and c["flavor"] == "phrygian"


def test_anchored_to_tonal_tonic_not_recentered():
    # bII relativo a A (Bb) em Lá menor → frígio relativo a A, sem virar centro Bb.
    c = detect_coloring("A", "minor", ["Am", "Bb", "Am", "Bb", "Am"])
    assert c is not None and c["flavor"] == "phrygian"


# --- 4.2 ausência / assimetria ------------------------------------------------


def test_bVII_in_minor_is_not_mixolydian():
    # Am com G (bVII diatônico do eólio): NÃO é mixolídio.
    assert detect_coloring("A", "minor", ["Am", "G", "Am", "G", "Am"]) is None


def test_single_neapolitan_bII_is_not_phrygian():
    # Um único bII em menor (napolitano/SubV pontual) → sem coloração.
    assert detect_coloring("A", "minor", ["Am", "Dm", "Bb", "Am"]) is None


def test_major_IV_in_minor_is_not_dorian_v1():
    # IV maior em menor (sinal dórico) NÃO dispara — dórico fora da v1.
    assert detect_coloring("D", "minor", ["Dm", "G", "Dm", "G", "Dm"]) is None


def test_plain_diatonic_major_is_silent():
    assert detect_coloring("C", "major", ["C", "F", "G7", "C"]) is None


# --- 4.3 anti-regressão do falso-positivo (eólias do corpus) ------------------


def test_aeolian_with_diatonic_bVII_and_single_bII_silent():
    # i-iv-V-i menor com bVII diatônico e um bII napolitano isolado: silêncio.
    c = detect_coloring("A", "minor", ["Am", "Dm", "E7", "Am", "G", "Am", "Bb", "Am"])
    assert c is None
