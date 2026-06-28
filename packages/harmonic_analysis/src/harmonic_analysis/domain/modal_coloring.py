"""Coloração modal: overlay descritivo sobre a análise tonal.

Resume, no nível da peça, os empréstimos modais já presentes na harmonia — ancorado
na tônica do `detect_key`, SEM re-estimar centro e SEM alterar tom/grau/função. É o
oposto do detector de modo removido (`fix-or-remove-church-mode`): aqui a coloração é
estritamente aditiva e omissível.

v1 cobre dois sabores, com gatilhos ASSIMÉTRICOS calibrados contra o ground-truth de
Chediak (Vol. I, pp. 124-127):

- **mixolídio (só sobre tom MAIOR):** sinais não-diatônicos = bVII maior e v menor
  (Chediak dá I7/Vm7/bVII7M como cadenciais, p. 124). Dispara por bVII→I, ou bVII
  recorrente (≥2 distintos), ou v menor recorrente (≥2 distintos).
- **frígio (só sobre tom MENOR):** dispara só pela cadência estrutural bII→i (≥2). Um
  bII pontual/recorrente-sem-cadência é napolitano/SubV tonal, não cor frígia.

Dórico fica fora da v1: compartilha coleção com o mixolídio, então separá-los exige
detecção de centro modal (3b, bloqueado).
"""

from __future__ import annotations

from typing import List, Optional, Sequence

from cifra_core.theory import Note
from cifra_core.theory.chord_parse import Third, parse

# Offsets característicos (semitons acima da tônica tonal).
_BVII = 10  # bVII (maior) — empréstimo mixolídio no maior
_VMIN = 7   # v (menor)    — dominante menor, mixolídio no maior
_BII = 1    # bII (maior)  — frígio no menor (cadência bII→i)


def _offsets(symbols: Sequence[str], tonic_pc: int):
    """(offset_da_tônica, é_maior, é_menor) por acorde; None quando não parseia."""
    out = []
    for s in symbols:
        try:
            p = parse(s)
            off = (p.root.pitch_class - tonic_pc) % 12
            out.append((off, p.third == Third.MAJOR, p.third == Third.MINOR))
        except Exception:
            out.append(None)
    return out


def _distinct(offs, target, want_major) -> int:
    """Ocorrências NÃO-adjacentes do grau (colapsa repetição de seção)."""
    idxs = [
        i
        for i, oq in enumerate(offs)
        if oq and oq[0] == target and (oq[1] if want_major else oq[2])
    ]
    n, prev = 0, -2
    for i in idxs:
        if i != prev + 1:
            n += 1
        prev = i
    return n


def _cadence_to_tonic(offs, char_off, want_major) -> List[int]:
    """Índices onde o grau característico (qualidade certa) resolve na tônica."""
    hits = []
    for i in range(len(offs) - 1):
        a, b = offs[i], offs[i + 1]
        if a and b and a[0] == char_off and (a[1] if want_major else a[2]) and b[0] == 0:
            hits.append(i)
    return hits


def detect_coloring(
    key_note: str, mode: str, symbols: Sequence[str]
) -> Optional[dict]:
    """Coloração modal da peça, ancorada na tônica tonal, ou None.

    `key_note` é a tônica tonal (ex.: "C", "Bb"); `mode` é "major"|"minor";
    `symbols` são os acordes da peça. Retorna `{flavor, evidence, where}` ou None.
    """
    try:
        tonic_pc = Note.parse(key_note).pitch_class
    except Exception:
        return None
    offs = _offsets(symbols, tonic_pc)

    if mode == "major":
        bvii_cad = _cadence_to_tonic(offs, _BVII, want_major=True)
        bvii_n = _distinct(offs, _BVII, want_major=True)
        vmin_n = _distinct(offs, _VMIN, want_major=False)
        if bvii_cad or bvii_n >= 2 or vmin_n >= 2:
            evidence: List[str] = []
            where: List[int] = []
            if bvii_cad:
                evidence.append(f"cadência bVII→I ({len(bvii_cad)}×)")
                where += bvii_cad
            if bvii_n >= 2:
                evidence.append(f"bVII recorrente ({bvii_n}×)")
            if vmin_n >= 2:
                evidence.append(f"v menor recorrente ({vmin_n}×)")
            return {"flavor": "mixolydian", "evidence": evidence, "where": sorted(set(where))}

    elif mode == "minor":
        bii_cad = _cadence_to_tonic(offs, _BII, want_major=True)
        if len(bii_cad) >= 2:
            return {
                "flavor": "phrygian",
                "evidence": [f"cadência estrutural bII→i ({len(bii_cad)}×)"],
                "where": sorted(set(bii_cad)),
            }

    return None
