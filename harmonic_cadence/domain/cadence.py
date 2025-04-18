from typing import Dict, List, Set

from .constants import CADENCE_PATTERNS


def analyze_cadences(
    degree_seq: List[str], mode: str, all_chords: List[str]
) -> Dict[str, Set[str]]:
    """
    Analisa e retorna as cadências encontradas na sequência de graus.
    Retorna um dicionário com o nome da cadência e os pares de acordes que a compõem.
    """
    patterns = (
        CADENCE_PATTERNS["major"] if mode == "major" else CADENCE_PATTERNS["minor"]
    )

    unique_cadences = {
        "Autêntica": set(),
        "Plagal": set(),
        "Interrompida": set(),
        "Meia-cadência": set(),
    }

    for i in range(len(degree_seq) - 1):
        pair = (degree_seq[i], degree_seq[i + 1])
        chord_pair = f"{all_chords[i]} → {all_chords[i+1]}"
        # Autêntica
        if pair == patterns["authentic"]:
            unique_cadences["Autêntica"].add(chord_pair)
        # Plagal
        elif pair == patterns["plagal"]:
            unique_cadences["Plagal"].add(chord_pair)
        # Interrompida
        elif pair == patterns["deceptive"]:
            unique_cadences["Interrompida"].add(chord_pair)
        # Meia-cadência (qualquer grau para dominante)
        elif patterns["half"][1] in pair[1]:
            unique_cadences["Meia-cadência"].add(chord_pair)
    return unique_cadences
