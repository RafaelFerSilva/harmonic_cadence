"""Cifragem romana: numeral + qualidade + inversão (pelo baixo) + aplicados."""

from __future__ import annotations

from typing import Optional

from cifra_core.theory import Note

from harmonic_analysis.domain.chord import Chord

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]


def _degree_index(analysis, root_pc: int) -> Optional[int]:
    if root_pc in analysis.scale_pcs:
        return analysis.scale_pcs.index(root_pc)
    return None


def _case(roman: str, chord: Chord) -> str:
    if chord.quality in ("minor", "diminished", "half-diminished"):
        return roman.lower()
    return roman


def _quality_mark(chord: Chord) -> str:
    """Marca de qualidade da tríade (não inclui a sétima)."""
    q = chord.quality
    if q == "diminished":
        return "°"
    if q == "half-diminished":
        return "ø"
    if q == "augmented":
        return "+"
    return ""


def _seventh_suffix(chord: Chord) -> str:
    """Sufixo da sétima em posição fundamental (substituído pela figura nas inversões)."""
    if not chord.properties.has_seventh:
        return ""
    low = chord.symbol.lower()
    if chord.quality not in ("diminished", "half-diminished") and (
        "maj" in low or "7m" in low
    ):
        return "maj7"
    return "7"


def _inversion_figure(chord: Chord) -> str:
    bass = chord.properties.bass
    if not bass:
        return ""
    try:
        root_pc = Note.parse(chord.root).pitch_class
        bass_pc = Note.parse(bass).pitch_class
    except Exception:
        return ""
    interval = (bass_pc - root_pc) % 12
    if interval == 0:
        return ""  # fundamental no baixo
    has7 = chord.properties.has_seventh
    third = interval in (3, 4)
    fifth = interval == 7
    seventh = interval in (10, 11)
    if not has7:
        if third:
            return "6"
        if fifth:
            return "6/4"
    else:
        if third:
            return "6/5"
        if fifth:
            return "4/3"
        if seventh:
            return "4/2"
    return ""  # baixo não é nota do acorde


def roman_numeral(
    chord: Chord, analysis, next_chord: Optional[Chord] = None
) -> str:
    """Numeral romano do acorde no contexto da análise."""
    # Acorde aplicado (dominante secundário) tem notação própria.
    if chord.is_dominant_seventh and next_chord:
        ni = analysis._get_interval(chord.root, next_chord.root)
        target_is_tonic = analysis._get_interval(next_chord.root, analysis.key) == 0
        if ni == 5 and not target_is_tonic:
            return f"V7/{analysis.get_degree(next_chord)}"

    try:
        root_pc = Note.parse(chord.root).pitch_class
    except Exception:
        return "?"
    idx = _degree_index(analysis, root_pc)
    if idx is None:
        # Diminuto de 7ª cromático ascendente: numeral de grau alterado (#I°7,
        # #II°7, #IV°7, #V°7, #VI°7) — V7(b9) rootless resolvendo um semitom
        # acima (preserva a marca °7; a função/glosa vem do analyze_function).
        if chord.quality == "diminished":
            try:
                key_pc = Note.parse(analysis.key).pitch_class
            except Exception:
                return "?"
            sharp_degree = {1: "I", 3: "II", 6: "IV", 8: "V", 10: "VI"}
            deg = sharp_degree.get((root_pc - key_pc) % 12)
            if deg is not None:
                return f"#{deg.lower()}°7"
        return "?"  # não-diatônico (Camada 2 cobre diatônico + aplicados)

    base = _case(ROMAN[idx], chord) + _quality_mark(chord)
    figure = _inversion_figure(chord)
    # Nas inversões a figura de baixo cifrado já implica a sétima; na fundamental
    # usa-se o sufixo de sétima (7/maj7).
    return base + (figure if figure else _seventh_suffix(chord))
