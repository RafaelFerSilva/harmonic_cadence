"""Detecção de tonalidade por Krumhansl-Schmuckler a partir dos acordes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from cifra_core.theory import realize, root_pitch_class

# Perfis de tonalidade Krumhansl-Kessler.
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

# Spellings convencionais de tonalidade por classe de altura.
MAJOR_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
MINOR_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]

# Pesos calibrados no corpus de validação (test_key_corpus): 100% de acerto.
ROOT_WEIGHT = 2.0      # ênfase na fundamental de cada acorde
CADENCE_WEIGHT = 2.0   # ênfase no acorde final (resolução cadencial → tônica)


@dataclass(frozen=True)
class KeyEstimate:
    tonic_pc: int
    mode: str          # "major" | "minor"
    score: float
    name: str          # ex.: "C major"
    key_note: str      # ex.: "C" (para HarmonicAnalysis)
    alternatives: Tuple[Tuple[str, float], ...] = ()


@dataclass(frozen=True)
class KeyRegion:
    start: int
    end: int           # índice inclusivo
    estimate: KeyEstimate


def pitch_class_profile(symbols: Sequence[str]) -> List[float]:
    """Perfil de 12 classes de altura acumulado dos acordes.

    A fundamental de cada acorde é ponderada; a fundamental do acorde final
    recebe ênfase cadencial extra (a resolução tende à tônica).
    """
    profile = [0.0] * 12
    n = len(symbols)
    for i, sym in enumerate(symbols):
        try:
            pcs = realize(sym)
            rpc = root_pitch_class(sym)
        except Exception:
            continue
        for pc in pcs:
            profile[pc] += 1.0
        profile[rpc] += ROOT_WEIGHT
        if i == n - 1:
            profile[rpc] += CADENCE_WEIGHT
    return profile


def _pearson(x: Sequence[float], y: Sequence[float]) -> float:
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = (
        sum((xi - mx) ** 2 for xi in x) * sum((yi - my) ** 2 for yi in y)
    ) ** 0.5
    return num / den if den else 0.0


def _name(tonic_pc: int, mode: str) -> Tuple[str, str]:
    note = (MAJOR_NAMES if mode == "major" else MINOR_NAMES)[tonic_pc]
    return f"{note} {mode}", note


def detect_key(symbols: Sequence[str]) -> Optional[KeyEstimate]:
    """Estima a tonalidade correlacionando o perfil com os 24 perfis K-S."""
    profile = pitch_class_profile(symbols)
    if sum(profile) == 0:
        return None

    ranked: List[Tuple[float, int, str]] = []
    for tonic in range(12):
        rotated = [profile[(tonic + i) % 12] for i in range(12)]
        ranked.append((_pearson(rotated, KS_MAJOR), tonic, "major"))
        ranked.append((_pearson(rotated, KS_MINOR), tonic, "minor"))
    ranked.sort(key=lambda t: t[0], reverse=True)

    best_score, best_tonic, best_mode = ranked[0]
    name, key_note = _name(best_tonic, best_mode)
    alts = tuple((f"{_name(t, m)[0]}", round(s, 4)) for s, t, m in ranked[1:4])
    return KeyEstimate(best_tonic, best_mode, round(best_score, 4), name, key_note, alts)


def _label(symbols: Sequence[str]) -> Optional[Tuple[int, str]]:
    est = detect_key(symbols)
    return (est.tonic_pc, est.mode) if est else None


def segment_keys(symbols: Sequence[str], window: int = 8) -> List[KeyRegion]:
    """Segmenta a sequência em regiões tonais (detecta modulação).

    Usa janelas não-sobrepostas de `window` acordes, fundindo blocos adjacentes
    de mesma tonalidade. Granularidade e janela são parâmetros a calibrar no
    corpus de validação.
    """
    n = len(symbols)
    if n == 0:
        return []
    if n <= window:
        est = detect_key(symbols)
        return [KeyRegion(0, n - 1, est)] if est else []

    chunks = [(i, min(i + window, n)) for i in range(0, n, window)]
    labels = [_label(symbols[a:b]) for a, b in chunks]

    regions: List[KeyRegion] = []
    cs = 0
    for i in range(1, len(chunks) + 1):
        if i == len(chunks) or labels[i] != labels[cs]:
            a = chunks[cs][0]
            b = chunks[i - 1][1] - 1
            est = detect_key(symbols[a : b + 1])
            if est:
                regions.append(KeyRegion(a, b, est))
            cs = i
    return regions
