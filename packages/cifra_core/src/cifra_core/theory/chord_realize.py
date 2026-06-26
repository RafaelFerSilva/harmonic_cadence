from __future__ import annotations

import re
from typing import FrozenSet

from cifra_core.theory.pitch import Note

_ROOT_RE = re.compile(r"^([A-G](?:##|bb|x|#|b)?)")


def _split_root(symbol: str) -> tuple[Note, str]:
    m = _ROOT_RE.match(symbol.strip())
    if not m:
        raise ValueError(f"Acorde sem fundamental reconhecível: {symbol!r}")
    return Note.parse(m.group(1)), symbol[m.end():]


def _intervals_for(quality: str) -> set[int]:
    """Mapeia o sufixo de qualidade para os intervalos (em semitons) da fundamental.

    Pragmático e afinado para a notação de cifra brasileira (`7M` = maj7, `°` = dim).
    """
    q = quality
    low = q.lower()

    # Meio-diminuto e diminuto primeiro (mais específicos).
    if "m7b5" in low or "ø" in q:
        return {0, 3, 6, 10}
    if "dim" in low or "°" in q or "º" in q:
        return {0, 3, 6, 9} if "7" in q else {0, 3, 6}
    if "aug" in low or "+" in q:
        return {0, 4, 8, 10} if "7" in q else {0, 4, 8}

    # Sétima maior: 'maj' ou a notação BR '7M' (sete-então-M).
    maj7 = ("maj" in low) or ("7m" in low)
    # Terça menor: um 'm' que não venha de 'maj' nem do '7M'.
    minor = "m" in low.replace("maj", "").replace("7m", "")

    tones: set[int] = {0, 3, 7} if minor else {0, 4, 7}

    if maj7:
        tones.add(11)
    elif "7" in q:
        tones.add(10)
    if "6" in q:
        tones.add(9)
    if "9" in q:
        tones.add(2)
    if "11" in q:
        tones.add(5)
    if "13" in q:
        tones.add(9)

    # Alterações.
    if "b5" in low:
        tones.discard(7)
        tones.add(6)
    if "#5" in low or "+5" in low:
        tones.discard(7)
        tones.add(8)
    if "b9" in low:
        tones.add(1)
    if "#9" in low:
        tones.add(3)
    if "#11" in low:
        tones.add(6)
    if "b13" in low:
        tones.add(8)

    return tones


def realize(symbol: str) -> FrozenSet[int]:
    """Realiza um símbolo de acorde em seu conjunto de classes de altura (0..11).

    Independente de tonalidade: spelling é uma etapa posterior.
    """
    root, quality = _split_root(symbol)
    rpc = root.pitch_class
    return frozenset((rpc + i) % 12 for i in _intervals_for(quality))


def root_pitch_class(symbol: str) -> int:
    """Classe de altura da fundamental do acorde."""
    root, _ = _split_root(symbol)
    return root.pitch_class
