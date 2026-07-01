"""Taxonomia de cadências (Chediak Vol. I, XXXII, pp. 109-111).

Cinco cadências — perfeita, imperfeita, plagal, meia-cadência, deceptiva — mais a
autêntica (perfeita precedida de subdominante). Classificação por posição de grau
(`degree_base`), válida em maior e menor; perfeita vs imperfeita pela inversão do
baixo (o que a cifra estabelece).
"""

from typing import Dict, List, Optional, Sequence, Set

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmonic_function import degree_base


def _inverted(symbol: str) -> bool:
    """True se o acorde está invertido (baixo cifrado ≠ fundamental)."""
    try:
        c = Chord(symbol)
        return c.properties.bass is not None and c.properties.bass != c.root
    except Exception:
        return False


def _modulates(chord_keys: Optional[Sequence[Optional[str]]], i: int) -> bool:
    """True se os acordes `i` e `i+1` caem em regiões tonais de tons diferentes."""
    if not chord_keys or i + 1 >= len(chord_keys):
        return False
    a, b = chord_keys[i], chord_keys[i + 1]
    return a is not None and b is not None and a != b


def _non_repose(code: Optional[str]) -> bool:
    """True se o código de função é uma TENSÃO (não-repouso) — dominante, SubV ou diminuto.

    Uma cadência é a combinação das funções "D" e "T" (Chediak XXXII, p.110); o alvo precisa
    FUNCIONAR como repouso. As funções de tensão começam com `D` (`D`, `D2`, `Dsec`, `Daux`,
    `Dext`, `Dim`) ou `Sub` (`SubV`, `Sub2`); nenhuma de repouso começa assim (`T`, `SD`, `Emp`,
    `Modal`, `Blues`, `Outro`)."""
    if not code:
        return False
    return code.startswith("D") or code.startswith("Sub")


def analyze_cadences(
    degree_seq: List[str],
    mode: str,
    all_chords: List[str],
    chord_keys: Optional[Sequence[Optional[str]]] = None,
    function_codes: Optional[Sequence[Optional[str]]] = None,
) -> Dict[str, Set[str]]:
    """Cadências encontradas na sequência (Chediak). `mode` é mantido por
    compatibilidade; a classificação é por posição de grau. `chord_keys` (tom de
    cada acorde, da região tonal) separa a deceptiva diatônica da modulante.

    `function_codes` (a saída do coder de função, alinhada por índice a `all_chords`) torna a
    cadência coerente com a função: nos ramos que resolvem na tônica (a família autêntica/plagal),
    um alvo de função NÃO-REPOUSO (`_non_repose`) é resolução direta (Chediak XXXIII, p.111), não
    cadência — o par é SUPRIMIDO. Sem `function_codes`, a classificação é grau-puro (compat)."""
    cad: Dict[str, Set[str]] = {
        "Perfeita": set(),
        "Autêntica": set(),
        "Imperfeita": set(),
        "Plagal": set(),
        "Meia-cadência": set(),
        "Deceptiva diatônica": set(),
        "Deceptiva modulante": set(),
    }
    n = min(len(degree_seq), len(all_chords))
    for i in range(n - 1):
        a = degree_base(degree_seq[i])
        b = degree_base(degree_seq[i + 1])
        pair = f"{all_chords[i]} → {all_chords[i + 1]}"

        # Coerência D→T (Chediak XXXII): uma cadência só resolve na tônica quando o alvo
        # FUNCIONA como repouso. Se o "I"-por-grau funciona como dominante/diminuto, é
        # resolução direta (XXXIII), não cadência — suprime a família autêntica/plagal.
        target_non_repose = function_codes is not None and _non_repose(
            function_codes[i + 1] if i + 1 < len(function_codes) else None
        )

        if b == "V" and a != "V":  # meia-cadência: descanso no dominante
            cad["Meia-cadência"].add(pair)
        elif a == "V" and b == "I":  # família autêntica (V→I)
            if target_non_repose:
                continue  # resolução direta (elo de cadeia), não cadência
            if _inverted(all_chords[i]) or _inverted(all_chords[i + 1]):
                cad["Imperfeita"].add(pair)
            else:
                cad["Perfeita"].add(pair)
                if i >= 1 and degree_base(degree_seq[i - 1]) in ("IV", "II"):
                    cad["Autêntica"].add(
                        f"{all_chords[i - 1]} → {all_chords[i]} → {all_chords[i + 1]}"
                    )
        elif a == "VII" and b == "I":  # VII→I enfraquece → imperfeita
            if target_non_repose:
                continue
            cad["Imperfeita"].add(pair)
        elif a in ("IV", "II") and b == "I":  # plagal (IV→I ou IIm→I)
            if target_non_repose:
                continue
            cad["Plagal"].add(pair)
        elif a == "V" and b != "I":  # deceptiva: V → não-tônica
            if _modulates(chord_keys, i):
                cad["Deceptiva modulante"].add(pair)
            else:
                cad["Deceptiva diatônica"].add(pair)
    return cad
