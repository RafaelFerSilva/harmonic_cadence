# infra/utils.py

import re
from typing import List


def is_tablature_line(line: str) -> bool:
    """
    Detecta linhas típicas de tablatura, como:
    E|---, B|---, G|---, D|---, A|---, etc.
    """
    return bool(re.match(r"^[EBGDA][|:].*[-0-9hpb/\\~]+", line.strip()))


def is_riff_or_section(line: str) -> bool:
    """
    Detecta marcações de partes, riffs, solos, intros, tabs, etc.
    Exemplo: [Intro], [Tab - Solo], (Riff 1), etc.
    """
    line_stripped = line.strip()
    return (
        bool(re.match(r"^\[.*\]$", line_stripped))
        or "(Riff" in line_stripped
        or "Tab" in line_stripped
        or "Solo" in line_stripped
        or "Guitarra" in line_stripped
        or "Parte" in line_stripped
    )


def filter_cifra_lines(lines: List[str]) -> List[str]:
    """
    Remove linhas de tablatura, marcações de partes e outras linhas não musicais.
    """
    filtered = []
    for line in lines:
        if is_tablature_line(line):
            continue
        if is_riff_or_section(line):
            continue
        filtered.append(line)
    return filtered
