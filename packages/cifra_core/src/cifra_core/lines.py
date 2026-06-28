import re
import unicodedata
from typing import List

# Linhas estruturais/ruído a descartar (a cifra musical é preservada).
_TAB_RE = re.compile(r"^[eEbBgGdDaA]\|")          # tablatura: E|---, B|---, ...
_TOM_RE = re.compile(r"^tom:", re.IGNORECASE)     # marcação de tom
_PART_RE = re.compile(r"^Parte \d+ de \d+$")      # "Parte 1 de 2"
_SECTION_RE = re.compile(r"^\[.*\]$")             # [Intro], [Refrão], ...
_RIFF_RE = re.compile(r"\(Riff", re.IGNORECASE)   # (Riff 1), ...
_AFIN_RE = re.compile(r"(afinac|drop\s+[a-g]|capotraste)", re.IGNORECASE)  # tuning lines


def clean_text(text: str) -> str:
    """Normaliza (NFC) e remove espaços nas pontas."""
    return unicodedata.normalize("NFC", text.strip())


def decode_unicode_escape(text: str) -> str:
    """Decodifica sequências de escape unicode remanescentes, se houver."""
    if "\\u" in text:
        try:
            return bytes(text, "utf-8").decode("unicode_escape")
        except Exception:
            pass
    return text


def _is_noise(line: str) -> bool:
    """True para linhas estruturais que não fazem parte da harmonia."""
    if not line:
        return True
    if _TAB_RE.match(line):
        return True
    if _TOM_RE.match(line):
        return True
    if _PART_RE.match(line):
        return True
    if _SECTION_RE.match(line):
        return True
    if _RIFF_RE.search(line):
        return True
    if _AFIN_RE.search(line):
        return True
    return False


def clean_cifra_lines(lines: List[str]) -> List[str]:
    """
    Filtro canônico de linhas de cifra — fonte única para scraper e analisador.

    Remove tablaturas, marcadores de seção/estrutura ([Intro], "Parte N de M",
    "tom:"), linhas vazias e duplicatas consecutivas; **preserva** linhas de
    acordes e de letra, na ordem original.

    Idempotente: aplicar novamente sobre a saída devolve a mesma lista.
    """
    out: List[str] = []
    prev = None
    for raw in lines:
        line = clean_text(decode_unicode_escape(raw))
        if _is_noise(line):
            continue
        if line == prev:
            continue
        out.append(line)
        prev = line
    return out
