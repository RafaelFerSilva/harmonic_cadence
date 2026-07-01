import re
import unicodedata
from enum import Enum
from typing import List

from cifra_core.chords import ChordPattern

# Linhas estruturais/ruído a descartar (a cifra musical é preservada).
_TAB_RE = re.compile(r"^[eEbBgGdDaA]\|")          # tablatura: E|---, B|---, ...
_TOM_RE = re.compile(r"^tom:", re.IGNORECASE)     # marcação de tom
_PART_RE = re.compile(r"^Parte \d+ de \d+$")      # "Parte 1 de 2"
_SECTION_RE = re.compile(r"^\[.*\]$")             # [Intro], [Refrão], ...
_RIFF_RE = re.compile(r"\(Riff", re.IGNORECASE)   # (Riff 1), ...
_AFIN_RE = re.compile(r"(afinac|drop\s+[a-g]|capotraste)", re.IGNORECASE)  # tuning lines


class LineKind(Enum):
    """Tipo de uma linha de cifra: acordes, letra ou marcador de seção."""

    CHORD = "chord"
    LYRIC = "lyric"
    SECTION = "section"


# Rótulo inline tipo "Introdução:", "Refrão:" — descartado antes de medir densidade.
_LABEL_RE = re.compile(r"^[^\W\d_][\w]*\s*:\s*", re.UNICODE)
# Tokens de decoração que não contam no denominador da densidade.
_DECOR = frozenset({"/", "|", "//", "-", "—", "·"})


def is_chord_token(token: str) -> bool:
    """True sse o regex canônico casa o token INTEIRO (não só um prefixo).

    `re.fullmatch` é o que distingue um acorde de uma palavra de letra: `"C"`/`"Am7"`/`"G/B"`
    casam por completo; `"Brasil"`/`"Com"`/`"Feio"` não (o resto não é gramática de acorde).
    Usar `parse()` aqui não serve — `parse("Brasil")` casa a raiz `B` e ignora `"rasil"`.
    """
    return bool(token) and ChordPattern.CHORD.fullmatch(token) is not None


# Caracteres de decoração (separador de compasso, hífen de alinhamento) — ignorados no resíduo.
_RESIDUE_DECOR = re.compile(r"[\s/|%\-—·]")


def malformed_chord_token(token: str) -> bool:
    """True sse o token é um acorde MALFORMADO — claramente pretendido como acorde, mas não parseável.

    Um acorde malformado (ex.: `D9/S`, baixo `/S` inválido) deve ser REPORTADO como notação não
    identificada, nunca descartado em silêncio nem chutado (não emitir o prefixo `D9`). Condições
    (todas): (a) NÃO é acorde completo (`is_chord_token` falso); (b) tem **prefixo de acorde
    válido** (o regex casa no início); (c) o **resto começa com `/` ou `(`** — uma tentativa de
    baixo/tensão (escopo que poupa palavra de letra: `Brasil` → resto `rasil`); (d) sobra **lixo**
    após remover TODOS os acordes válidos e a decoração (poupa acordes colados por barra:
    `Gm7(11)///Gb7(#11)///` → resíduo vazio → NÃO malformado).
    """
    if is_chord_token(token):
        return False
    m = ChordPattern.CHORD.match(token)
    if not m or m.end() == 0:
        return False
    rest = token[m.end():]
    if not rest or rest[0] not in "/(":
        return False
    residue = _RESIDUE_DECOR.sub("", ChordPattern.CHORD.sub(" ", token))
    return residue != ""


def classify_line(line: str, *, threshold: float = 0.6) -> LineKind:
    """Classifica a linha por DENSIDADE de acordes válidos (fonte única de desambiguação).

    Uma linha é CHORD quando a razão (tokens-que-são-acorde / tokens-não-decoração) atinge o
    `threshold`; senão é LYRIC. Um rótulo de seção sozinho (`"Introdução:"`) vira SECTION; um
    rótulo seguido de acordes (`"Introdução: Dm7 G7"`) é classificado pelo resto. Leitura
    pura: não muta nem remove a linha.
    """
    s = line.strip()
    if not s:
        return LineKind.SECTION
    body = _LABEL_RE.sub("", s, count=1)
    had_label = body != s
    tokens = [t for t in body.split() if t not in _DECOR]
    if not tokens:
        return LineKind.SECTION if had_label else LineKind.LYRIC
    # Posição-de-acorde = acorde válido OU malformado (`D9/S`): conta o malformado para a
    # linha não sumir (senão a densidade cai e os acordes válidos dela são descartados).
    chords = sum(1 for t in tokens if is_chord_token(t) or malformed_chord_token(t))
    return LineKind.CHORD if chords / len(tokens) >= threshold else LineKind.LYRIC


# Token ambíguo: raiz nua de uma letra (A-G), que colide com palavra de letra (E="e").
_BARE_RE = re.compile(r"[A-G]$")


def extract_chords_from_lines(
    lines: List[str],
    *,
    known_chords: "frozenset[str] | set[str] | None" = None,
    unidentified: "list[str] | None" = None,
    threshold: float = 0.6,
) -> List[str]:
    """Extrai os símbolos de acorde lendo SÓ linhas de cifra (caminho único de extração).

    Linhas LYRIC/SECTION não contribuem token nenhum. Itera por TOKEN: um token de acorde
    MALFORMADO (`D9/S`) é coletado em `unidentified` (se fornecido) e NÃO é extraído — nunca
    chuta o prefixo `D9` nem descarta em silêncio. Um token AMBÍGUO — raiz nua de uma letra
    (`A`-`G`), que colide com palavra de letra — só é admitido se houver `known_chords` e ele
    estiver no vocabulário; sem `known_chords`, basta estar numa linha CHORD. Os demais tokens
    passam por `find_all` (separador de compasso, baixo invertido e acordes colados intactos).
    """
    out: List[str] = []
    for line in lines:
        if classify_line(line, threshold=threshold) is not LineKind.CHORD:
            continue
        for token in line.split():
            if token in _DECOR:
                continue
            if malformed_chord_token(token):
                if unidentified is not None:
                    unidentified.append(token)
                continue
            for sym in ChordPattern.find_all(token):
                if not sym:
                    continue
                if (
                    _BARE_RE.fullmatch(sym)
                    and known_chords is not None
                    and sym not in known_chords
                ):
                    continue
                out.append(sym)
    return out


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
