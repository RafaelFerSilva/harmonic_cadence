"""Path D (bracket ii-V) do gate de qualidade do `detect_key`.

A armadilha do ii-V: o K-S pega o V e o achador funcional pega o ii — nenhum pega o I.
O bracket ("detect=V de X E funcional=ii de X") é o ÚNICO discriminador seguro (o #7
provou que todo gate estrutural regride). Sequências REAIS de bolinha-de-sabao e rio
(hardcoded, não dependem de `cifras/`), + guards unitários.
"""

import glob
import os
import re

import pytest

from harmonic_analysis.domain.key_detection import detect_key, _ii_v_bracket_path

# Sequências reais extraídas do corpus (o vamp ii-V onde o K-S pegava o V).
BOLINHA = [
    "Dm7", "G7(9)", "Em7", "A7(9)", "Dm7", "G7(9)", "Em7", "A7(9)", "Dm7", "G7(9)",
    "Em7", "A7(9)", "Dm7", "G7(9)", "C9", "Dm7", "G7(9)", "Em7", "A7(9)", "Dm7",
    "G7(9)", "Em7", "A7(9)", "Dm7", "G7(9)", "Em7", "A7(9)", "Dm7", "G7(9)", "C9",
    "Bb6", "Ab6", "C7M", "Fm7", "Bb7(9)", "Eb7M", "Fm7", "Bb7(9)", "Eb7M", "Dm7",
    "G7(9)", "Em7", "A7(9)", "Dm7", "G7(9)", "Gm7(9)", "C7(13)", "F7M", "Fm6",
    "Em7", "A7(13)", "Ab7(13)", "G7(13)",
]
RIO = [
    "Gm7", "C7(9)", "Gm7", "C7(9)", "C7(b9)", "F7M", "Bb7(9)", "Am7", "D7(b9)",
    "Gm7", "C7(9)", "C7(b9)", "F7M", "Bb7(9)", "Am7", "D7(b9)", "G7M", "Gº",
    "F7M", "Fº", "E9(b13)", "Em7(9)", "A7(13)", "Cm7", "D7(b9)", "Gm7", "C7(9)",
    "Bbm7", "Eb7(9)", "Am7", "D7(b9)", "Gm7", "C7(9)", "Gm7", "C7(9)",
]
# Progressão diatônica limpa em Dó: o funcional pega o PRÓPRIO Dó (não o ii) — controle.
C_MAJOR_CLEAN = ["C", "F", "G", "C", "Am", "Dm", "G", "C"]


def test_bolinha_ii_v_trap_corrected_to_the_I():
    # K-S pegava o V (Sol); o funcional pega o ii (Dm); o I é Dó.
    est = detect_key(BOLINHA)
    assert (est.tonic_pc, est.mode) == (0, "major")  # Dó maior (Path D)


def test_rio_ii_v_trap_corrected_to_the_I():
    est = detect_key(RIO)
    assert (est.tonic_pc, est.mode) == (5, "major")  # Fá maior (Path D)


def test_path_d_returns_the_I_when_bracketed():
    # Chamando o path direto com o V (Sol) como palpite do K-S → corrige p/ Dó.
    assert _ii_v_bracket_path(BOLINHA, (7, "major")) == (0, "major")


def test_path_d_does_not_fire_when_functional_is_not_the_ii():
    # Controle: numa peça diatônica limpa o funcional é o próprio Dó (não o ii de Dó),
    # então o bracket NÃO dispara mesmo forçando o palpite no V (Sol).
    assert _ii_v_bracket_path(C_MAJOR_CLEAN, (7, "major")) is None


def test_path_d_needs_at_least_two_resolutions():
    # Uma única G7→C (sem repetição) não satisfaz o guard de ≥2 resoluções.
    assert _ii_v_bracket_path(["Dm7", "G7", "C7M", "F", "Am"], (7, "major")) is None


def test_clean_c_major_still_detects_c_major():
    # Anti-regressão: o Path D não toca a detecção correta trivial.
    est = detect_key(C_MAJOR_CLEAN)
    assert (est.tonic_pc, est.mode) == (0, "major")


# ── Anti-regressão sobre o corpus real (skip em CI: cifras/ é gitignored) ──────
_CODE = re.compile(r"```(.*?)```", re.S)
_MAN = re.compile(r"\*\*Acordes Utilizados:\*\*\s*(.+)")
_TICK = re.compile(r"`([^`]+)`")


def _corpus_chords(path: str):
    from cifra_core import cifra_from_text, extract_chords_from_lines

    text = open(path, encoding="utf-8").read()
    body = "\n".join(_CODE.findall(text)) or text
    m = _MAN.search(text)
    known = frozenset(_TICK.findall(m.group(1))) if m else frozenset()
    return extract_chords_from_lines(cifra_from_text(body).cifra, known_chords=known)


@pytest.mark.skipif(
    not glob.glob("cifras/*.md"), reason="corpus local ausente (cifras/ gitignored)"
)
@pytest.mark.parametrize(
    "slug,expected",
    [
        # armadilha ii-V corrigida pelo Path D:
        ("bolinha-de-sabao", (0, "major")),   # → Dó
        ("menina", (0, "major")),             # → Dó
        ("rio", (5, "major")),                # → Fá
        # risco de falso-positivo (o Path D NÃO pode tocar): agree + detect-certo:
        ("ceu-e-mar", (5, "major")),          # agree, Fá (não vira Bb)
        ("pouca-duracao", (10, "major")),     # agree, Bb (não vira Eb)
        ("feitinha-pro-poeta", (2, "major")),  # detect-certo, Ré (não vira Sol)
        ("chora-tua-tristeza", (2, "major")),  # detect-certo, Ré (não vira Sol)
    ],
)
def test_path_d_change_set_is_exactly_the_three_traps(slug, expected):
    path = f"cifras/{slug}.md"
    if not os.path.exists(path):
        pytest.skip(f"{slug} ausente")
    est = detect_key(_corpus_chords(path))
    assert (est.tonic_pc, est.mode) == expected
