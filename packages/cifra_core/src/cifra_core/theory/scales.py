from __future__ import annotations

from typing import List

from cifra_core.theory.pitch import LETTER_PC, LETTERS, Note

# Padrões de modo: semitons de cada grau a partir da tônica.
MODE_PATTERNS = {
    "ionian": [0, 2, 4, 5, 7, 9, 11],
    "major": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian": [0, 2, 3, 5, 7, 8, 10],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11],
}


def build_scale(tonic: Note, mode: str = "major") -> List[Note]:
    """Constrói a escala/modo a partir da tônica, com spelling diatônico correto.

    Cada grau recebe a próxima letra (uma letra por grau), e o acidente é
    escolhido para casar a classe de altura do padrão — então F maior dá `Bb`
    (não `A#`) e G mixolídio dá `F` natural.
    """
    if mode not in MODE_PATTERNS:
        raise ValueError(f"Modo desconhecido: {mode!r}")
    pattern = MODE_PATTERNS[mode]
    start = LETTERS.index(tonic.letter)

    scale: List[Note] = []
    for i, semis in enumerate(pattern):
        letter = LETTERS[(start + i) % 7]
        target_pc = (tonic.pitch_class + semis) % 12
        acc = (target_pc - LETTER_PC[letter]) % 12
        if acc > 6:  # escolhe o acidente mais próximo (ex.: 11 -> -1)
            acc -= 12
        scale.append(Note(letter, acc))
    return scale
