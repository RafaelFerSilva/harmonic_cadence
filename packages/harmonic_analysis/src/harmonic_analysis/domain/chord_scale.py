"""Escala-acorde e tensões: escala recomendada, tensões disponíveis e avoid notes."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from cifra_core.theory import Note, build_scale, realize

from harmonic_analysis.domain.chord import Chord

# Grau diatônico (em maior) → modo da escala-acorde.
DEGREE_SCALE = [
    "ionian",
    "dorian",
    "phrygian",
    "lydian",
    "mixolydian",
    "aeolian",
    "locrian",
]

# Rótulo da tensão pelo intervalo (semitons) acima da fundamental.
TENSION_LABEL = {1: "b9", 2: "9", 3: "#9", 5: "11", 6: "#11", 8: "b13", 9: "13"}

# Posições (semitons da tônica) de acordes dominantes que pedem lídio b7
# (Chediak, pág. 113): II7, IV7, bVI7, bVII7, VII7. As demais → mixolídio.
_LYDIAN_DOM_POS = {2, 5, 8, 10, 11}


def recommended_scale(chord: Chord, analysis) -> Optional[Tuple[str, List[Note]]]:
    """Escala-acorde recomendada (modo + notas), pelo grau/função no contexto."""
    try:
        root = Note.parse(chord.root)
    except Exception:
        return None
    if chord.quality == "half-diminished":
        return "locrian", build_scale(root, "locrian")
    if chord.is_dominant_seventh:
        # Acorde dominante: escala dominante pela posição (Chediak, p. 113),
        # não a escala da tríade diatônica da fundamental.
        try:
            key_pc = Note.parse(analysis.key).pitch_class
            pos = (root.pitch_class - key_pc) % 12
            mode = "lydian_dominant" if pos in _LYDIAN_DOM_POS else "mixolydian"
        except Exception:
            mode = "mixolydian"
        return mode, build_scale(root, mode)
    if root.pitch_class not in analysis.scale_pcs:
        return None  # não-diatônico (Camada 2 cobre o diatônico)
    mode = DEGREE_SCALE[analysis.scale_pcs.index(root.pitch_class)]
    return mode, build_scale(root, mode)


def tensions_and_avoids(chord: Chord, scale_notes: List[Note]) -> Tuple[List[str], List[str]]:
    """Tensões disponíveis (tom acima de nota do acorde) e avoid (semitom acima)."""
    try:
        root_pc = Note.parse(chord.root).pitch_class
    except Exception:
        return [], []
    chord_pcs = set(realize(chord.symbol))
    tensions: List[str] = []
    avoids: List[str] = []
    for n in scale_notes:
        pc = n.pitch_class
        if pc in chord_pcs:
            continue
        label = TENSION_LABEL.get((pc - root_pc) % 12)
        if not label:
            continue
        if ((pc - 1) % 12) in chord_pcs:        # semitom acima de nota do acorde
            avoids.append(label)
        elif ((pc - 2) % 12) in chord_pcs:      # tom acima de nota do acorde
            tensions.append(label)
    return tensions, avoids


def analyze_chord(chord: Chord, analysis) -> Optional[Dict]:
    """Mapeamento escala-acorde + tensões/avoid de um acorde, ou None se não-diatônico."""
    rec = recommended_scale(chord, analysis)
    if rec is None:
        return None
    mode, scale = rec
    tensions, avoids = tensions_and_avoids(chord, scale)
    return {
        "chord": chord.symbol,
        "scale": f"{chord.root} {mode}",
        "tensions": tensions,
        "avoid": avoids,
    }
