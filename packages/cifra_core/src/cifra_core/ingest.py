"""Ingestão de cifra a partir de texto local — o adaptador de entrada NÃO-Cifra-Club.

Converte texto cru de acordes (um `.txt`, um upload, uma progressão autoral) no mesmo
`Cifra` normalizado que o `SongProvider` produz, para cair no MESMO motor de análise.
Reusa a filtragem canônica e idempotente `clean_cifra_lines` (aplicada UMA vez, honrando
o contrato do `analysis_service`); a extração de acordes segue sendo do motor
(`ChordPattern`), não daqui. Sem tom da fonte (`key=""`): a tonalidade é detectada dos
acordes — a fuga da "armadilha dos metadados".
"""

from __future__ import annotations

from cifra_core.lines import clean_cifra_lines, clean_text
from cifra_core.models import Cifra


def cifra_from_text(text: str, *, artist: str = "", title: str = "") -> Cifra:
    """Texto cru de acordes → `Cifra` normalizada (linhas limpas, `key=""`).

    `artist`/`title` são metadados opcionais (um arquivo local não tem identidade de
    catálogo); ausentes, o motor aplica seu fallback "Desconhecido". A filtragem de
    ruído (marcadores de seção, tablatura, linhas vazias) vem de `clean_cifra_lines`,
    a mesma do provider — uma fonte de verdade, idempotente.
    """
    lines = clean_cifra_lines(clean_text(text or "").splitlines())
    return Cifra(
        artist=artist,
        name=title,
        cifra=tuple(lines),
        key="",  # sem tom da fonte: a tonalidade nasce do detect_key sobre os acordes
    )
