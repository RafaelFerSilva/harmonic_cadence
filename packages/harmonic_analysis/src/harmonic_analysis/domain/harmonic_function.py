"""Classificação diatônica de função harmônica (fonte: Chediak, pp. 91-96).

Função tonal por posição de grau, qualidade funcional (forte/meio-forte/fraco)
e o campo diatônico menor sobre as três escalas (harmônica, natural, melódica
real). Núcleo determinístico e reutilizável; o `analyze_function` e o parser
probabilístico podem consumi-lo.
"""

from __future__ import annotations

import re
from typing import Optional

from cifra_core.theory import Note, realize, root_pitch_class

# Função tonal por grau (Chediak, pág. 96): I/III/VI = tônica,
# II/IV = subdominante, V/VII = dominante.
FUNCTION_BY_DEGREE = {
    "I": "T", "III": "T", "VI": "T",
    "II": "SD", "IV": "SD",
    "V": "D", "VII": "D",
}

# Qualidade funcional (Chediak, pág. 92): principais I/IV/V são fortes;
# substitutos do IV e V (II, VII) meio-fortes; substitutos do I (III, VI) fracos.
STRENGTH_BY_DEGREE = {
    "I": "strong", "IV": "strong", "V": "strong",
    "II": "medium", "VII": "medium",
    "III": "weak", "VI": "weak",
}

_ROMAN_RE = re.compile(r"^[b#]?(VII|VI|IV|V|III|II|I)", re.IGNORECASE)

# As três escalas menores como classes de altura a partir da tônica (semitons).
_MINOR_SCALE_PATTERNS = {
    "natural": (0, 2, 3, 5, 7, 8, 10),
    "harmonic": (0, 2, 3, 5, 7, 8, 11),
    "melodic": (0, 2, 3, 5, 7, 9, 11),  # melódica real (sobe e desce igual)
}

_MINOR_FUNCTION_BY_POS = {
    0: "T", 2: "SD", 3: "T", 5: "SD", 7: "D", 8: "T", 10: "D",
}


def degree_base(label: str) -> Optional[str]:
    """Numeral romano de posição (I..VII), ignorando acidente e qualidade."""
    if not label:
        return None
    m = _ROMAN_RE.match(label.strip())
    return m.group(1).upper() if m else None


def tonal_function(degree_label: str) -> Optional[str]:
    """Função tonal (T/SD/D) de um grau diatônico maior."""
    return FUNCTION_BY_DEGREE.get(degree_base(degree_label) or "")


def functional_strength(degree_label: str) -> Optional[str]:
    """Qualidade funcional (strong/medium/weak) de um grau."""
    return STRENGTH_BY_DEGREE.get(degree_base(degree_label) or "")


def minor_field_pcs(tonic: str) -> frozenset[int]:
    """Campo diatônico menor: união das três escalas menores (Chediak, pp. 94-96)."""
    tpc = Note.parse(tonic).pitch_class
    pcs: set[int] = set()
    for pattern in _MINOR_SCALE_PATTERNS.values():
        pcs |= {(tpc + i) % 12 for i in pattern}
    return frozenset(pcs)


def is_diatonic_minor(chord_symbol: str, tonic: str) -> bool:
    """True se o acorde é diatônico a *alguma* das três escalas menores."""
    try:
        return realize(chord_symbol) <= minor_field_pcs(tonic)
    except Exception:
        return False


def minor_function(chord_symbol: str, tonic: str) -> Optional[str]:
    """Função tonal de um acorde numa tonalidade menor.

    O `Vm7` da menor natural não tem função tonal (sem sensível) — Chediak,
    pág. 96, nota: retorna ``None``.
    """
    from harmonic_analysis.domain.chord import Chord

    try:
        pos = (root_pitch_class(chord_symbol) - Note.parse(tonic).pitch_class) % 12
    except Exception:
        return None
    if pos == 7 and not Chord(chord_symbol).is_dominant_seventh:
        return None  # Vm7 natural: sem função tonal
    return _MINOR_FUNCTION_BY_POS.get(pos)
