"""Escala-acorde e tensões: escala recomendada, tensões disponíveis e avoid notes."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from cifra_core.theory import Fifth, Note, build_scale, parse, realize

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

# Classe de altura → nome soletrado (bemóis canônicos, padrão do projeto).
_PC_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Posições (semitons da tônica) de acordes dominantes que pedem lídio b7
# (Chediak, pág. 113): II7, IV7, bVI7, bVII7, VII7. As demais → mixolídio.
_LYDIAN_DOM_POS = {2, 5, 8, 10, 11}


def _altered_dominant_scale(chord: Chord) -> Optional[str]:
    """Escala de um dominante ALTERADO pela alteração presente (Chediak P5).

    Tem precedência sobre o mapa posicional. Retorna None se não há alteração de
    quinta nem de nona (cai no mapa posicional mixolídio/lídio b7)."""
    try:
        p = parse(chord.symbol)
    except Exception:
        return None
    if p.fifth is Fifth.AUGMENTED:  # #5
        return "whole_tone"
    if p.fifth is Fifth.DIMINISHED:  # b5
        return "lydian_dominant"
    t = p.tensions
    if 6 in t:  # #11
        return "lydian_dominant"
    if 1 in t:  # b9
        return "altered" if 3 in t else "diminished"
    if 3 in t:  # #9
        return "altered"
    return None


def recommended_scale(
    chord: Chord, analysis, next_chord: Optional[Chord] = None
) -> Optional[Tuple[str, List[Note]]]:
    """Escala-acorde recomendada (modo + notas), pelo grau/função no contexto."""
    try:
        root = Note.parse(chord.root)
    except Exception:
        return None
    if chord.quality == "half-diminished":
        return "locrian", build_scale(root, "locrian")
    if chord.quality == "diminished":
        # Diminuto de 7ª = V7(b9) sem fundamental (Chediak p. 90): a escala-acorde é
        # a diminuta (octatônica). A coleção correta é a do dominante implícito, uma
        # 3ª maior abaixo da fundamental escrita (B°7 → G7(b9) → octatônica de G);
        # o semitom-tom (build_scale "diminished") da implícita devolve exatamente
        # a octatônica que contém as notas do acorde.
        implied = Note.parse(_PC_NAMES[(root.pitch_class - 4) % 12])
        return "diminished", build_scale(implied, "diminished")
    if chord.is_dominant_seventh:
        # Dominante alterado: escala pela alteração (Chediak P5), com precedência.
        mode = _altered_dominant_scale(chord)
        if mode is None:
            # Dominante estendido (Chediak XXVIII(a), p.339): resolve em OUTRO
            # dominante por 4ªJ ascendente → mixolídio, independente da posição
            # (a regra específica do estendido vence o default posicional p.113).
            if (
                next_chord is not None
                and next_chord.is_dominant_seventh
                and analysis._get_interval(chord.root, next_chord.root) == 5
            ):
                mode = "mixolydian"
            else:
                # Sem alteração: escala dominante pela posição (Chediak, p. 113),
                # não a escala da tríade diatônica da fundamental.
                try:
                    key_pc = Note.parse(analysis.key).pitch_class
                    pos = (root.pitch_class - key_pc) % 12
                    mode = (
                        "lydian_dominant" if pos in _LYDIAN_DOM_POS else "mixolydian"
                    )
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


def analyze_chord(
    chord: Chord, analysis, next_chord: Optional[Chord] = None
) -> Optional[Dict]:
    """Mapeamento escala-acorde + tensões/avoid de um acorde, ou None se não-diatônico."""
    rec = recommended_scale(chord, analysis, next_chord)
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
