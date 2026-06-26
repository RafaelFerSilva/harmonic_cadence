"""Modo (igreja) como centro tonal de 1ª classe.

Detecta o modo a partir da coleção diatônica dos acordes e do centro tonal
(o "final" — último acorde), conservador por padrão (cai em tonal).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from cifra_core.theory import Note, build_scale, realize, root_pitch_class

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]
PC_TO_NAME = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# Grau característico de cada modo (relativo ao maior).
CHARACTERISTIC = {
    "mixolydian": "bVII",
    "dorian": "IV",
    "phrygian": "bII",
    "lydian": "II",
    "locrian": "bII",
}

# Cadência característica de cada modo (par de graus modais).
MODAL_CADENCE = {
    "mixolydian": ("bVII", "I"),
    "phrygian": ("bII", "I"),
    "dorian": ("IV", "I"),
    "lydian": ("II", "I"),
    "aeolian": ("v", "I"),
}

# Nota característica de cada modo (Chediak, pp. 122-125).
CHARACTERISTIC_NOTE = {
    "ionian": None,
    "dorian": "6",
    "phrygian": "b2",
    "lydian": "#4",
    "mixolydian": "b7",
    "aeolian": "b6",
    "locrian": "b2/b6",
}

# Acordes cadenciais característicos (tétrades) e acordes a evitar, por modo —
# seleção curatorial do Chediak (pp. 122-125), não derivável do campo.
MODAL_CADENTIAL = {
    "ionian": [],
    "dorian": ["IIm7", "IV7", "bVII7M"],
    "phrygian": ["bII7M", "bVIIm7"],
    "lydian": ["II7", "V7M", "VIIm7"],
    "mixolydian": ["I7", "Vm7", "bVII7M"],
    "aeolian": ["IVm7", "bVI7M", "bVII7"],
    "locrian": [],
}

MODAL_AVOID = {
    "ionian": [],
    "dorian": ["VIm7(b5)"],
    "phrygian": ["Vm7(b5)", "bIII7"],
    "lydian": ["#IVm7(b5)"],
    "mixolydian": ["IIIm7(b5)"],
    "aeolian": ["IIm7(b5)"],
    "locrian": [],
}

# Qualidade da tétrade pelos intervalos (3ª, 5ª, 7ª) acima da fundamental.
_QUALITY_BY_INTERVALS = {
    (3, 6, 9): "dim7",
    (3, 6, 10): "m7b5",
    (3, 7, 10): "m7",
    (3, 7, 11): "m(maj7)",
    (4, 7, 10): "7",
    (4, 7, 11): "maj7",
    (4, 8, 11): "maj7#5",
}


@dataclass(frozen=True)
class ModeInfo:
    tonic_pc: int
    tonic: str
    mode: str  # mixolydian | dorian | phrygian | lydian | locrian


def _collection(symbols: Sequence[str]) -> set:
    pcs: set = set()
    for s in symbols:
        try:
            pcs |= set(realize(s))
        except Exception:
            continue
    return pcs


def _final_tonic_pc(symbols: Sequence[str]) -> Optional[int]:
    for s in reversed(symbols):
        try:
            return root_pitch_class(s)
        except Exception:
            continue
    return None


def detect_mode(symbols: Sequence[str]) -> Optional[ModeInfo]:
    """Classifica um modo de igreja, ou None quando a peça é tonal (maior/menor)."""
    if not symbols:
        return None
    coll = _collection(symbols)
    t = _final_tonic_pc(symbols)
    if t is None or not coll:
        return None

    def has(off: int) -> bool:
        return ((t + off) % 12) in coll

    def lacks(off: int) -> bool:
        return ((t + off) % 12) not in coll

    mode: Optional[str] = None
    if has(4) and has(10) and lacks(11):          # 3ª maior + b7, sem sensível
        mode = "mixolydian"
    elif has(4) and has(6) and lacks(5):          # 3ª maior + #4, sem 4ª justa
        mode = "lydian"
    elif has(3) and has(1) and has(6) and lacks(7):  # 3ª menor + b2 + b5
        mode = "locrian"
    elif has(3) and has(1):                        # 3ª menor + b2
        mode = "phrygian"
    elif has(3) and has(9) and lacks(8) and lacks(1):  # 3ª menor + ♮6, sem b6/b2
        mode = "dorian"

    return ModeInfo(t, PC_TO_NAME[t], mode) if mode else None


def modal_degree(root_pc: int, tonic: str, mode: str) -> Optional[str]:
    """Grau modal de uma classe de altura (ex.: F em G mixolídio → bVII)."""
    tonic_note = Note.parse(tonic)
    scale = build_scale(tonic_note, mode)
    major = build_scale(tonic_note, "major")
    for i, n in enumerate(scale):
        if n.pitch_class == root_pc:
            roman = ROMAN[i]
            diff = (n.pitch_class - major[i].pitch_class) % 12
            if diff == 11:
                return "b" + roman
            if diff == 1:
                return "#" + roman
            return roman
    return None


def characteristic_degree(mode: str) -> Optional[str]:
    return CHARACTERISTIC.get(mode)


def modal_cadences(degree_seq: Sequence[str], mode: str) -> List[Tuple[str, str]]:
    """Cadências modais encontradas na sequência de graus modais."""
    pat = MODAL_CADENCE.get(mode)
    if not pat:
        return []
    return [
        pat
        for i in range(len(degree_seq) - 1)
        if (degree_seq[i], degree_seq[i + 1]) == pat
    ]


def _tetrad_quality(scale: Sequence[Note], i: int) -> str:
    """Qualidade da tétrade empilhada sobre o grau `i` da escala."""
    root = scale[i % 7]
    third = scale[(i + 2) % 7]
    fifth = scale[(i + 4) % 7]
    seventh = scale[(i + 6) % 7]
    rpc = root.pitch_class
    key = (
        (third.pitch_class - rpc) % 12,
        (fifth.pitch_class - rpc) % 12,
        (seventh.pitch_class - rpc) % 12,
    )
    return _QUALITY_BY_INTERVALS.get(key, "?")


def modal_field(tonic: str, mode: str) -> List[Tuple[str, str]]:
    """Os 7 acordes diatônicos (grau modal, qualidade) de um modo.

    Derivado da escala (`build_scale`), correto por construção — substitui o
    campo hardcoded por dado verificável contra Chediak (pp. 122-125).
    """
    tonic_note = Note.parse(tonic)
    scale = build_scale(tonic_note, mode)
    field: List[Tuple[str, str]] = []
    for i in range(7):
        degree = modal_degree(scale[i].pitch_class, tonic, mode)
        field.append((degree or ROMAN[i], _tetrad_quality(scale, i)))
    return field
