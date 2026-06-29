"""Rótulos PT-BR para a apresentação.

O modelo interno é em inglês canônico (`phrygian`, `minor`, `lydian_dominant`);
estes helpers traduzem **só na exibição**. Mantêm a letra do acorde (A–G, a
cifra BR) e traduzem apenas a palavra.
"""

from __future__ import annotations

_MODE_PT = {"major": "maior", "minor": "menor"}

_CHURCH_MODE_PT = {
    "ionian": "jônico",
    "dorian": "dórico",
    "phrygian": "frígio",
    "lydian": "lídio",
    "mixolydian": "mixolídio",
    "aeolian": "eólio",
    "locrian": "lócrio",
}

_QUALITY_PT = {
    "major": "maior",
    "minor": "menor",
    "dominant": "dominante",
    "diminished": "diminuto",
    "half-diminished": "meio-diminuto",
    "augmented": "aumentado",
    "suspended": "suspenso",
    "power": "quinta",
    "unknown": "indefinido",
}

# Escalas: modos gregos + escalas dominantes. "diminuta"/"alterada" no feminino
# (escala), distinto de "diminuto" (acorde).
_SCALE_PT = {
    **_CHURCH_MODE_PT,
    "major": "maior",
    "minor": "menor",
    "lydian_dominant": "lídio b7",
    "whole_tone": "hexafônica",
    "diminished": "diminuta",
    "altered": "alterada",
    "harmonic_minor": "menor harmônica",
    "melodic_minor": "menor melódica",
}


def mode_pt(mode: str) -> str:
    """Qualidade do tom: major→maior, minor→menor."""
    return _MODE_PT.get(mode, mode)


def church_mode_pt(mode: str) -> str:
    """Modo grego: phrygian→frígio, mixolydian→mixolídio, ..."""
    return _CHURCH_MODE_PT.get(mode, mode)


# Flavors de coloração que viram NOME de modo no display. Só mixolídio/frígio têm
# assinatura mecânica que o `detect_coloring` emite; eólio é menor natural (sem
# rótulo) e dórico depende de detecção de centro modal (curadoria, não algoritmo).
_NAMEABLE_FLAVORS = ("mixolydian", "phrygian")


def modal_mode_name(key_note: str, flavor: str) -> str:
    """Funde a tônica tonal com o modo grego do flavor de coloração.

    Promoção de DISPLAY de um campo já computado (`modal_coloring.flavor`): não
    re-estima centro. `("D", "mixolydian") -> "D mixolídio"`. Flavor ausente,
    desconhecido ou não-nomeável → só a tônica tonal (sem inventar modo)."""
    if flavor in _NAMEABLE_FLAVORS:
        return f"{key_note} {_CHURCH_MODE_PT[flavor]}"
    return key_note


# Volumes do Chediak em algarismo romano (a citação sempre mostra "Vol. I").
_ROMAN = {1: "I", 2: "II", 3: "III"}

# Intervalo (semitons) → nome em PT-BR, p/ exibir o finalis modal de forma
# transposição-segura ("o modo dórico sobre a 5ª justa acima da tônica tonal").
_INTERVAL_PT = {
    1: "2ª menor",
    2: "2ª maior",
    3: "3ª menor",
    4: "3ª maior",
    5: "4ª justa",
    6: "trítono",
    7: "5ª justa",
    8: "6ª menor",
    9: "6ª maior",
    10: "7ª menor",
    11: "7ª maior",
}


def interval_pt(semitones: int) -> str:
    """Nome do intervalo (0..11 semitons) em PT-BR; `7` → '5ª justa'."""
    return _INTERVAL_PT.get(semitones % 12, "uníssono")


def format_citation(citation) -> str:
    """`Citation` → 'Almir Chediak, Harmonia & Improvisação, Vol. I, p. 125'.

    Fonte ÚNICA da string de citação (volume em romano), para que Markdown e HTML
    nunca divirjam. Consome o `Citation` tipado do corpus (`source/volume/page`)."""
    vol = _ROMAN.get(citation.volume, str(citation.volume))
    return f"{citation.source}, Vol. {vol}, p. {citation.page}"


def quality_pt(quality: str) -> str:
    """Qualidade do acorde: dominant→dominante, diminished→diminuto, ..."""
    return _QUALITY_PT.get(quality, quality)


def scale_pt(scale: str) -> str:
    """Nome de escala mantendo a fundamental: `G mixolydian`→`G mixolídio`."""
    parts = scale.split(" ", 1)
    if len(parts) == 2:
        return f"{parts[0]} {_SCALE_PT.get(parts[1], parts[1])}"
    return _SCALE_PT.get(scale, scale)
