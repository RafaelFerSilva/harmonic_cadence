"""Taxonomia de cadências (Chediak Vol. I, XXXII, pp. 109-111).

Cinco cadências — perfeita, imperfeita, plagal, meia-cadência, deceptiva — mais a
autêntica (perfeita precedida de subdominante). Classificação por posição de grau
(`degree_base`), válida em maior e menor; perfeita vs imperfeita pela inversão do
baixo (o que a cifra estabelece).
"""

from typing import Dict, List, Set

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmonic_function import degree_base


def _inverted(symbol: str) -> bool:
    """True se o acorde está invertido (baixo cifrado ≠ fundamental)."""
    try:
        c = Chord(symbol)
        return c.properties.bass is not None and c.properties.bass != c.root
    except Exception:
        return False


def analyze_cadences(
    degree_seq: List[str], mode: str, all_chords: List[str]
) -> Dict[str, Set[str]]:
    """Cadências encontradas na sequência (Chediak). `mode` é mantido por
    compatibilidade; a classificação é por posição de grau."""
    cad: Dict[str, Set[str]] = {
        "Perfeita": set(),
        "Autêntica": set(),
        "Imperfeita": set(),
        "Plagal": set(),
        "Meia-cadência": set(),
        "Deceptiva": set(),
    }
    n = min(len(degree_seq), len(all_chords))
    for i in range(n - 1):
        a = degree_base(degree_seq[i])
        b = degree_base(degree_seq[i + 1])
        pair = f"{all_chords[i]} → {all_chords[i + 1]}"

        if b == "V" and a != "V":  # meia-cadência: descanso no dominante
            cad["Meia-cadência"].add(pair)
        elif a == "V" and b == "I":  # família autêntica (V→I)
            if _inverted(all_chords[i]) or _inverted(all_chords[i + 1]):
                cad["Imperfeita"].add(pair)
            else:
                cad["Perfeita"].add(pair)
                if i >= 1 and degree_base(degree_seq[i - 1]) in ("IV", "II"):
                    cad["Autêntica"].add(
                        f"{all_chords[i - 1]} → {all_chords[i]} → {all_chords[i + 1]}"
                    )
        elif a == "VII" and b == "I":  # VII→I enfraquece → imperfeita
            cad["Imperfeita"].add(pair)
        elif a in ("IV", "II") and b == "I":  # plagal (IV→I ou IIm→I)
            cad["Plagal"].add(pair)
        elif a == "V" and b != "I":  # deceptiva: V → não-tônica
            cad["Deceptiva"].add(pair)
    return cad
