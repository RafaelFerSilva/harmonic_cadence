from __future__ import annotations

import re
from dataclasses import dataclass

# Classe de altura de cada letra natural.
LETTER_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LETTERS = "CDEFGAB"

_ACC_TO_INT = {"": 0, "#": 1, "##": 2, "x": 2, "b": -1, "bb": -2}
_INT_TO_ACC = {0: "", 1: "#", 2: "##", -1: "b", -2: "bb"}

_NOTE_RE = re.compile(r"^([A-Ga-g])(##|bb|x|#|b)?$")


@dataclass(frozen=True)
class Note:
    """Nota com ortografia preservada: letra + acidente, classe de altura derivada.

    `Db` e `C#` são `Note`s distintas que compartilham a mesma classe de altura.
    """

    letter: str          # 'A'..'G'
    accidental: int = 0  # -2..+2 (bb..##)

    def __post_init__(self):
        if self.letter not in LETTER_PC:
            raise ValueError(f"Letra inválida: {self.letter!r}")

    @property
    def pitch_class(self) -> int:
        return (LETTER_PC[self.letter] + self.accidental) % 12

    @classmethod
    def parse(cls, text: str) -> "Note":
        m = _NOTE_RE.match(text.strip())
        if not m:
            raise ValueError(f"Nota inválida: {text!r}")
        letter = m.group(1).upper()
        acc = _ACC_TO_INT[m.group(2) or ""]
        return cls(letter, acc)

    def __str__(self) -> str:
        return f"{self.letter}{_INT_TO_ACC.get(self.accidental, '')}"

    def __repr__(self) -> str:
        return f"Note('{self}')"


def interval_semitones(a: Note, b: Note) -> int:
    """Distância em semitons, ascendente, de `a` até `b` (0..11)."""
    return (b.pitch_class - a.pitch_class) % 12


def interval_magnitude(a: Note, b: Note) -> int:
    """Menor distância em semitons entre `a` e `b` (0..6)."""
    s = interval_semitones(a, b)
    return min(s, 12 - s)
