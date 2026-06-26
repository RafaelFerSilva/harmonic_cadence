"""Impressão digital de estilo (Camada 3 — D3).

Agrega features harmônicas sobre um conjunto de análises (corpus de um artista/
gênero) num vetor comparável: distribuição de funções, matriz de transição
função→função, contagem de cadências, uso modal e densidade de tensões. Compara
duas fingerprints por similaridade de cosseno. Determinístico e offline.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class Fingerprint:
    """Vetor de features harmônicas agregado de um corpus."""

    function_distribution: Dict[str, float]
    transition_matrix: Dict[str, Dict[str, float]]
    cadence_counts: Dict[str, int]
    modal_usage: float
    tension_density: float
    song_count: int

    def to_dict(self) -> dict:
        return {
            "function_distribution": self.function_distribution,
            "transition_matrix": {
                k: dict(v) for k, v in self.transition_matrix.items()
            },
            "cadence_counts": dict(self.cadence_counts),
            "modal_usage": round(self.modal_usage, 4),
            "tension_density": round(self.tension_density, 4),
            "song_count": self.song_count,
        }


def _functions_of(result: dict) -> List[str]:
    return [
        e.get("function_code")
        for e in result.get("harmonic_analysis", [])
        if e.get("function_code")
    ]


def build_fingerprint(results: Sequence[dict]) -> Fingerprint:
    """Constrói a fingerprint a partir de uma lista de análises (`result` dicts)."""
    func_counter: Counter = Counter()
    trans_counter: Dict[str, Counter] = defaultdict(Counter)
    cadence_counter: Counter = Counter()
    modal_songs = 0
    tension_hits = 0
    chord_total = 0
    song_count = 0

    for result in results:
        if not isinstance(result, dict) or not result.get("success", True):
            continue
        song_count += 1
        funcs = _functions_of(result)
        func_counter.update(funcs)
        for a, b in zip(funcs, funcs[1:]):
            trans_counter[a][b] += 1

        for name, pairs in (result.get("cadences") or {}).items():
            if pairs:
                cadence_counter[name] += len(pairs)

        if result.get("modal_analysis"):
            modal_songs += 1

        for cs in result.get("chord_scales") or []:
            chord_total += 1
            if cs.get("tensions"):
                tension_hits += 1

    # Distribuição de funções (perfil de probabilidade, soma 1).
    total_funcs = sum(func_counter.values())
    distribution = (
        {f: c / total_funcs for f, c in sorted(func_counter.items())}
        if total_funcs
        else {}
    )

    # Matriz de transição normalizada por linha.
    transition: Dict[str, Dict[str, float]] = {}
    for src, counter in trans_counter.items():
        row_total = sum(counter.values())
        transition[src] = {
            dst: counter[dst] / row_total for dst in sorted(counter)
        }

    modal_usage = modal_songs / song_count if song_count else 0.0
    tension_density = tension_hits / chord_total if chord_total else 0.0

    return Fingerprint(
        function_distribution=distribution,
        transition_matrix=transition,
        cadence_counts=dict(cadence_counter),
        modal_usage=modal_usage,
        tension_density=tension_density,
        song_count=song_count,
    )


def _feature_vector(fp: Fingerprint, keys: Sequence[str]) -> List[float]:
    """Achata distribuição + transição num vetor sobre um eixo de funções comum."""
    vec = [fp.function_distribution.get(k, 0.0) for k in keys]
    for src in keys:
        row = fp.transition_matrix.get(src, {})
        vec.extend(row.get(dst, 0.0) for dst in keys)
    vec.append(fp.modal_usage)
    vec.append(fp.tension_density)
    return vec


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def similarity(fp_a: Fingerprint, fp_b: Fingerprint) -> float:
    """Similaridade de cosseno (0..1) sobre o vetor de features concatenado."""
    keys = sorted(
        set(fp_a.function_distribution) | set(fp_b.function_distribution)
        | set(fp_a.transition_matrix) | set(fp_b.transition_matrix)
    )
    va = _feature_vector(fp_a, keys)
    vb = _feature_vector(fp_b, keys)
    return _cosine(va, vb)


def distance(fp_a: Fingerprint, fp_b: Fingerprint) -> float:
    """Distância = 1 − similaridade (0 para fingerprints idênticas)."""
    return 1.0 - similarity(fp_a, fp_b)


def jensen_shannon(fp_a: Fingerprint, fp_b: Fingerprint) -> float:
    """Divergência de Jensen-Shannon das distribuições de função (métrica alternativa)."""
    keys = sorted(set(fp_a.function_distribution) | set(fp_b.function_distribution))
    p = [fp_a.function_distribution.get(k, 0.0) for k in keys]
    q = [fp_b.function_distribution.get(k, 0.0) for k in keys]
    m = [(pi + qi) / 2 for pi, qi in zip(p, q)]

    def _kl(x: Sequence[float], y: Sequence[float]) -> float:
        total = 0.0
        for xi, yi in zip(x, y):
            if xi > 0 and yi > 0:
                total += xi * math.log2(xi / yi)
        return total

    return 0.5 * _kl(p, m) + 0.5 * _kl(q, m)


def compare(fp_a: Fingerprint, fp_b: Fingerprint) -> Dict[str, float]:
    """Resumo de comparação entre duas fingerprints."""
    return {
        "similarity": round(similarity(fp_a, fp_b), 4),
        "distance": round(distance(fp_a, fp_b), 4),
        "jensen_shannon": round(jensen_shannon(fp_a, fp_b), 4),
    }
