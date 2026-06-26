"""Parsing estruturado de símbolo de acorde (fonte: sistemática Chediak).

Um símbolo é decomposto em *slots* independentes por grau — terça, quinta,
sétima — mais tons acrescentados e tensões superiores. A realização em classes
de altura é **derivada** desses slots: uma fonte, duas vistas. Isto substitui o
antigo `_intervals_for` baseado em `contains()`, que dava falsos como contar a
9 dentro de `#9`.

Aceita os dois dialetos de acidente: Chediak `#/b` (canônico) e Cifra Club `±`
(`5+`=#5, `9-`=b9, `13-`=b13, `2-`=b9).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, List, Optional

from cifra_core.theory.pitch import Note

_ROOT_RE = re.compile(r"^([A-G](?:##|bb|x|#|b)?)")
_BASS_RE = re.compile(r"/([A-G](?:##|bb|x|#|b)?)\s*$")
_TOKEN_RE = re.compile(r"[#b]?\d+")


class Third(Enum):
    MAJOR = "major"
    MINOR = "minor"
    SUS2 = "sus2"
    SUS4 = "sus4"
    OMIT = "omit"


class Fifth(Enum):
    PERFECT = "perfect"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"


class Seventh(Enum):
    NONE = "none"
    MINOR = "minor"
    MAJOR = "major"
    DIMINISHED = "diminished"


class Category(Enum):
    """Categoria do acorde (Chediak, pp. 84-85), derivada dos slots."""

    MAJOR = "major"
    MINOR = "minor"
    DOMINANT = "dominant"
    DIMINISHED = "diminished"
    HALF_DIMINISHED = "half-diminished"
    AUGMENTED = "augmented"
    SUSPENDED = "suspended"
    POWER = "power"


_THIRD_SEMITONE = {Third.MAJOR: 4, Third.MINOR: 3, Third.SUS2: 2, Third.SUS4: 5}
_FIFTH_SEMITONE = {Fifth.PERFECT: 7, Fifth.DIMINISHED: 6, Fifth.AUGMENTED: 8}
_SEVENTH_SEMITONE = {Seventh.MINOR: 10, Seventh.MAJOR: 11, Seventh.DIMINISHED: 9}

# Token de estrutura superior -> semitons acima da fundamental.
_COLOR_SEMITONE = {
    "b9": 1, "9": 2, "#9": 3,
    "b2": 1, "#2": 3,
    "11": 5, "#11": 6, "b11": 4,
    "b13": 8, "13": 9, "#13": 10,
    "b6": 8, "6": 9, "#6": 10,
}


@dataclass(frozen=True)
class ParsedChord:
    root: Note
    bass: Optional[Note]
    third: Third
    fifth: Fifth
    seventh: Seventh
    added: FrozenSet[int]      # semitons de tons acrescentados (não implicam 7ª)
    tensions: FrozenSet[int]   # semitons de tensões superiores (sobre a 7ª)

    def pitch_classes(self) -> FrozenSet[int]:
        rpc = self.root.pitch_class
        intervals = {0}
        if self.third in _THIRD_SEMITONE:
            intervals.add(_THIRD_SEMITONE[self.third])
        intervals.add(_FIFTH_SEMITONE[self.fifth])
        if self.seventh in _SEVENTH_SEMITONE:
            intervals.add(_SEVENTH_SEMITONE[self.seventh])
        intervals |= self.added
        intervals |= self.tensions
        pcs = {(rpc + i) % 12 for i in intervals}
        if self.bass is not None:
            pcs.add(self.bass.pitch_class)
        return frozenset(pcs)

    def category(self) -> Category:
        if self.third in (Third.SUS2, Third.SUS4):
            return Category.SUSPENDED
        if self.third is Third.OMIT:
            return Category.POWER
        if self.third is Third.MINOR:
            if self.fifth is Fifth.DIMINISHED:
                if self.seventh is Seventh.MINOR:
                    return Category.HALF_DIMINISHED
                return Category.DIMINISHED
            return Category.MINOR
        # terça maior
        if self.fifth is Fifth.AUGMENTED and self.seventh is Seventh.NONE:
            return Category.AUGMENTED
        if self.seventh is Seventh.MINOR:
            return Category.DOMINANT  # trítono 3M-7m (Chediak, pág. 84)
        return Category.MAJOR


def parse(symbol: str) -> ParsedChord:
    """Decompõe um símbolo de acorde em slots (Chediak)."""
    s = symbol.strip()
    m = _ROOT_RE.match(s)
    if not m:
        raise ValueError(f"Acorde sem fundamental reconhecível: {symbol!r}")
    root = Note.parse(m.group(1))
    rest = s[m.end():]

    # Baixo invertido: barra seguida de NOTA (não de dígito, p/ não pegar 6/9).
    bass: Optional[Note] = None
    bm = _BASS_RE.search(rest)
    if bm:
        bass = Note.parse(bm.group(1))
        rest = rest[: bm.start()]

    # Dialeto Cifra Club: grau± -> #/b.
    rest = re.sub(r"(\d+)\+", r"#\1", rest)
    rest = re.sub(r"(\d+)-", r"b\1", rest)
    low = rest.lower()

    is_halfdim = "m7b5" in low or "m7(b5)" in low or "ø" in rest
    is_dim = (not is_halfdim) and ("dim" in low or "°" in rest or "º" in rest)
    is_aug = (not is_dim and not is_halfdim) and ("aug" in low or "+" in rest)
    has_sus2 = "sus2" in low
    has_sus = "sus" in low
    has_add = "add" in low
    has_maj7 = ("maj" in low) or bool(re.search(r"7m", low))

    tokens: List[str] = _TOKEN_RE.findall(rest)

    third: Optional[Third] = None
    fifth = Fifth.PERFECT
    colors: set[int] = set()
    power = False
    has_six = False
    has_ext = False
    has_seven_token = False

    for tok in tokens:
        if tok == "5":
            power = True
        elif tok == "b5":
            fifth = Fifth.DIMINISHED
        elif tok == "#5":
            fifth = Fifth.AUGMENTED
        elif tok == "7":
            has_seven_token = True
        elif tok == "6":
            has_six = True
            colors.add(9)
        elif tok == "4":
            third = Third.SUS4  # Chediak: o 4 suspende a terça (V7/4, pág. 105)
        elif tok == "2":
            if has_sus2:
                third = Third.SUS2
            else:
                colors.add(2)  # 2 nu = add9, terça mantida (Chediak: sem sus2)
        elif tok in _COLOR_SEMITONE:
            colors.add(_COLOR_SEMITONE[tok])
            if tok.lstrip("#b") in ("9", "11", "13"):
                has_ext = True

    # Slot da sétima (prioridade: dim > maj7 > 7 explícito > extensão implícita).
    if is_dim:
        seventh = Seventh.DIMINISHED
    elif is_halfdim:
        seventh = Seventh.MINOR
    elif has_maj7:
        seventh = Seventh.MAJOR
    elif has_seven_token:
        seventh = Seventh.MINOR
    elif has_ext and not has_six and not has_add:
        seventh = Seventh.MINOR  # extensão ímpar nua implica a 7ª (G9, G13)
    else:
        seventh = Seventh.NONE

    # Slot da terça / quinta.
    if is_dim or is_halfdim:
        third = Third.MINOR
        fifth = Fifth.DIMINISHED
    elif is_aug:
        if third is None:
            third = Third.MAJOR
        fifth = Fifth.AUGMENTED

    if third is None:
        if has_sus2:
            third = Third.SUS2
        elif has_sus:
            third = Third.SUS4
        elif power:
            third = Third.OMIT
        else:
            core = low
            for sub in ("maj", "sus", "dim", "aug", "add"):
                core = core.replace(sub, "")
            core = re.sub(r"7m", "", core)
            core = _TOKEN_RE.sub("", core)
            core = re.sub(r"[()/°ºø]", "", core)
            third = Third.MINOR if "m" in core else Third.MAJOR

    if seventh is Seventh.NONE:
        added, tensions = frozenset(colors), frozenset()
    else:
        added, tensions = frozenset(), frozenset(colors)

    return ParsedChord(root, bass, third, fifth, seventh, added, tensions)


def realize(symbol: str) -> FrozenSet[int]:
    """Realiza um símbolo de acorde em seu conjunto de classes de altura (0..11)."""
    return parse(symbol).pitch_classes()


def root_pitch_class(symbol: str) -> int:
    """Classe de altura da fundamental do acorde."""
    m = _ROOT_RE.match(symbol.strip())
    if not m:
        raise ValueError(f"Acorde sem fundamental reconhecível: {symbol!r}")
    return Note.parse(m.group(1)).pitch_class
