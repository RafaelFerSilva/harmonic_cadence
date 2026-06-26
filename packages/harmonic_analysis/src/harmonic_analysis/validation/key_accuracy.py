"""Harness de acurácia da detecção de tonalidade.

Compara o tom **detectado** com o **anotado** (o tom da fonte, ex.: Cifra Club),
com três métricas — modo, tônica exata e relativa-consciente — para que a
ambiguidade relativa maior/menor (a lição da Sina) vire número, não discussão.
"""

from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from cifra_core import ChordPattern
from cifra_core.theory import Note

from harmonic_analysis.domain.key_detection import detect_key

Key = Tuple[int, str]  # (classe de altura da tônica, "major" | "minor")

_KEY_RE = re.compile(r"^\s*([A-G][#b]?)\s*(m?)")
_TAG_RE = re.compile(r"<[^>]+>")


def parse_key(label: str) -> Optional[Key]:
    """Anotação de tom → (pc, modo). `"G"`→(7,'major'); `"Am"`→(9,'minor')."""
    if not label:
        return None
    m = _KEY_RE.match(label)
    if not m:
        return None
    try:
        pc = Note.parse(m.group(1)).pitch_class
    except Exception:
        return None
    return (pc, "minor" if m.group(2) == "m" else "major")


def is_relative(a: Key, b: Key) -> bool:
    """True se `a` e `b` são relativas (Dó maior ≡ Lá menor: tônica menor 3
    semitons abaixo da maior)."""
    (ta, ma), (tb, mb) = a, b
    if ma == "major" and mb == "minor":
        return tb == (ta - 3) % 12
    if ma == "minor" and mb == "major":
        return tb == (ta + 3) % 12
    return False


@dataclass(frozen=True)
class KeyEval:
    name: str
    annotated: Key
    detected: Key
    mode_ok: bool
    exact: bool
    relative: bool


def evaluate_song(
    name: str, chords: Iterable[str], annotated_key: str
) -> Optional[KeyEval]:
    """Avalia uma música; None se faltar anotação ou detecção."""
    annotated = parse_key(annotated_key)
    est = detect_key(list(chords))
    if annotated is None or est is None:
        return None
    detected: Key = (est.tonic_pc, est.mode)
    return KeyEval(
        name=name,
        annotated=annotated,
        detected=detected,
        mode_ok=annotated[1] == detected[1],
        exact=annotated == detected,
        relative=is_relative(annotated, detected),
    )


def evaluate_corpus(songs: Iterable[Tuple[str, Iterable[str], str]]) -> dict:
    """Métricas agregadas sobre `(nome, acordes, tom_anotado)`."""
    evals: List[KeyEval] = [
        e for s in songs if (e := evaluate_song(*s)) is not None
    ]
    n = len(evals)
    denom = n or 1
    return {
        "n": n,
        "mode_accuracy": sum(e.mode_ok for e in evals) / denom,
        "exact_accuracy": sum(e.exact for e in evals) / denom,
        "relative_aware_accuracy": sum(e.exact or e.relative for e in evals) / denom,
        "evals": evals,
    }


def load_corpus(directory: str) -> List[Tuple[str, List[str], str]]:
    """Carrega `data/*.json` que tenham `key` (anotação) — os demais ficam fora."""
    songs: List[Tuple[str, List[str], str]] = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        key = d.get("key") or ""
        if not key:
            continue
        chords = [
            s
            for line in d.get("cifra", [])
            for s in ChordPattern.find_all(_TAG_RE.sub("", line))
            if s
        ]
        songs.append((d.get("name", os.path.basename(path)), chords, key))
    return songs
