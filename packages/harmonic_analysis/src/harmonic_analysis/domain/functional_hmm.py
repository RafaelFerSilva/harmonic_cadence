"""Parsing funcional probabilístico (HMM + Viterbi).

Camada 3 — D1. Modela a função harmônica como uma cadeia de Markov oculta:
- **estados** = macro-funções (`T`, `SD`, `D`, `X`);
- **emissão** = ponte do analisador determinístico (Camada 2): a função que ele
  já atribui recebe a maior massa; alternativas plausíveis recebem o resto por
  priors de qualidade/função;
- **transição** = gramática funcional (D→T forte, SD→D forte, etc.).

Decodifica o caminho mais provável por **Viterbi** e mede confiança/alternativas
por **forward-backward**. Tudo determinístico e offline — complementa, não
substitui, a análise determinística existente.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmonic_function import functional_strength
from harmonic_analysis.domain.harmony import HarmonicAnalysis
from harmonic_analysis.domain.key_detection import detect_key

# Macro-funções (estados ocultos).
STATES: Tuple[str, ...] = ("T", "SD", "D", "X")

# Mapa código-de-função detalhado (Camada 2) → macro-função (estado do HMM).
# Dsec/SubV resolvem como dominante; D2/Sub2 são predominantes (preparam a D).
FUNCTION_MACRO: Dict[str, str] = {
    "T": "T",
    "SD": "SD",
    "D2": "SD",
    "Sub2": "SD",
    "D": "D",
    "Dsec": "D",
    "SubV": "D",
    "Emp": "X",
    "Modal": "X",
    "Dim": "X",
    "Crom": "X",
    "Outro": "X",
}

# Prior inicial (favorece a tônica).
INITIAL: Dict[str, float] = {"T": 0.40, "SD": 0.25, "D": 0.20, "X": 0.15}

# Transição: gramática funcional (linha = de, coluna = para). Cada linha soma 1.
TRANSITION: Dict[str, Dict[str, float]] = {
    "T": {"T": 0.30, "SD": 0.35, "D": 0.25, "X": 0.10},
    "SD": {"T": 0.10, "SD": 0.15, "D": 0.60, "X": 0.15},
    "D": {"T": 0.65, "SD": 0.05, "D": 0.15, "X": 0.15},
    "X": {"T": 0.35, "SD": 0.25, "D": 0.25, "X": 0.15},
}

# Massa de emissão da função escolhida pelo analisador determinístico.
PRIMARY_MASS = 0.70

# Massa primária ponderada pela força funcional do grau (Chediak, pág. 92):
# forte concentra mais no rótulo; fraca espalha mais nas alternativas. `None`
# (sem grau diatônico / parse só-código) usa o padrão — garante zero regressão.
STRENGTH_MASS: Dict[Optional[str], float] = {
    "strong": 0.82,
    "medium": PRIMARY_MASS,
    "weak": 0.55,
    None: PRIMARY_MASS,
}

# Como o resto (1 - PRIMARY_MASS) se distribui sobre as alternativas, por macro.
# Codifica ambiguidade idiomática: um vi (lido como T) também serve de
# predominante; um IV (SD) admite leitura de dominante secundária; etc.
ALT_PRIORS: Dict[str, Dict[str, float]] = {
    "T": {"T": 0.0, "SD": 0.5, "D": 0.2, "X": 0.3},
    "SD": {"T": 0.2, "SD": 0.0, "D": 0.5, "X": 0.3},
    "D": {"T": 0.5, "SD": 0.1, "D": 0.0, "X": 0.4},
    "X": {"T": 0.4, "SD": 0.3, "D": 0.3, "X": 0.0},
}


@dataclass(frozen=True)
class ChordFunction:
    """Função decidida para um acorde, com confiança e alternativas."""

    chord: str
    function: str  # macro-função escolhida (Viterbi)
    label: str  # rótulo detalhado do analisador determinístico (ex.: "Dsec")
    confidence: float  # posterior da macro-função escolhida (0..1)
    alternatives: List[Tuple[str, float]]  # (macro, prob) ordenado desc.


@dataclass(frozen=True)
class FunctionalParse:
    """Resultado do parsing funcional probabilístico."""

    path: List[str]  # caminho de macro-funções (Viterbi)
    chords: List[ChordFunction]

    def to_dict(self) -> dict:
        return {
            "path": list(self.path),
            "chords": [
                {
                    "chord": cf.chord,
                    "function": cf.function,
                    "label": cf.label,
                    "confidence": round(cf.confidence, 4),
                    "alternatives": [
                        {"function": f, "probability": round(p, 4)}
                        for f, p in cf.alternatives
                    ],
                }
                for cf in self.chords
            ],
        }


def transition_prob(src: str, dst: str) -> float:
    """Probabilidade de transição da gramática funcional `src → dst`."""
    return TRANSITION[src][dst]


def _emission(macro: str, strength: Optional[str] = None) -> Dict[str, float]:
    """Emissão para um acorde de macro `macro`, ponderada pela força funcional."""
    primary = STRENGTH_MASS.get(strength, PRIMARY_MASS)
    rest = 1.0 - primary
    alt = ALT_PRIORS[macro]
    e = {s: rest * alt[s] for s in STATES}
    e[macro] += primary
    return e


def _viterbi(emissions: Sequence[Dict[str, float]]) -> List[str]:
    """Caminho de estados mais provável (Viterbi, em log para estabilidade)."""
    if not emissions:
        return []

    def lg(x: float) -> float:
        return math.log(x) if x > 0 else float("-inf")

    # Inicialização.
    delta = {s: lg(INITIAL[s]) + lg(emissions[0][s]) for s in STATES}
    back: List[Dict[str, str]] = []

    for t in range(1, len(emissions)):
        new_delta: Dict[str, float] = {}
        ptr: Dict[str, str] = {}
        for dst in STATES:
            best_src, best_val = STATES[0], float("-inf")
            for src in STATES:
                val = delta[src] + lg(transition_prob(src, dst))
                if val > best_val:
                    best_val, best_src = val, src
            new_delta[dst] = best_val + lg(emissions[t][dst])
            ptr[dst] = best_src
        delta = new_delta
        back.append(ptr)

    # Término + backtrack.
    last = max(STATES, key=lambda s: delta[s])
    path = [last]
    for ptr in reversed(back):
        last = ptr[last]
        path.append(last)
    path.reverse()
    return path


def _forward_backward(
    emissions: Sequence[Dict[str, float]],
) -> List[Dict[str, float]]:
    """Marginais posteriores por posição (forward-backward com normalização)."""
    n = len(emissions)
    if n == 0:
        return []

    # Forward (escalonado).
    alpha: List[Dict[str, float]] = []
    a0 = {s: INITIAL[s] * emissions[0][s] for s in STATES}
    alpha.append(_normalize(a0))
    for t in range(1, n):
        prev = alpha[t - 1]
        cur = {
            dst: emissions[t][dst]
            * sum(prev[src] * transition_prob(src, dst) for src in STATES)
            for dst in STATES
        }
        alpha.append(_normalize(cur))

    # Backward (escalonado).
    beta: List[Dict[str, float]] = [dict.fromkeys(STATES, 1.0) for _ in range(n)]
    for t in range(n - 2, -1, -1):
        nxt = beta[t + 1]
        cur = {
            src: sum(
                transition_prob(src, dst) * emissions[t + 1][dst] * nxt[dst]
                for dst in STATES
            )
            for src in STATES
        }
        beta[t] = _normalize(cur)

    # Posterior ∝ alpha · beta.
    posteriors = []
    for t in range(n):
        merged = {s: alpha[t][s] * beta[t][s] for s in STATES}
        posteriors.append(_normalize(merged))
    return posteriors


def _normalize(dist: Dict[str, float]) -> Dict[str, float]:
    total = sum(dist.values())
    if total <= 0:
        return dict.fromkeys(STATES, 1.0 / len(STATES))
    return {s: dist[s] / total for s in STATES}


def parse_codes(
    function_codes: Sequence[str],
    chord_symbols: Sequence[str],
    strengths: Optional[Sequence[Optional[str]]] = None,
) -> FunctionalParse:
    """Parsing probabilístico a partir dos códigos de função determinísticos.

    `strengths` (opcional) pondera a emissão pela força funcional de cada grau;
    sem ela, o modelo emite como o não-ponderado (sem regressão).
    """
    macros = [FUNCTION_MACRO.get(code, "X") for code in function_codes]
    emissions = [
        _emission(m, strengths[i] if strengths and i < len(strengths) else None)
        for i, m in enumerate(macros)
    ]
    path = _viterbi(emissions)
    posteriors = _forward_backward(emissions)

    chords: List[ChordFunction] = []
    for i, sym in enumerate(chord_symbols):
        chosen = path[i]
        post = posteriors[i]
        alts = sorted(
            ((s, p) for s, p in post.items() if s != chosen),
            key=lambda kv: (-kv[1], kv[0]),
        )
        alts = [(s, p) for s, p in alts if p >= 0.05][:2]
        chords.append(
            ChordFunction(
                chord=sym,
                function=chosen,
                label=function_codes[i] if i < len(function_codes) else chosen,
                confidence=post[chosen],
                alternatives=alts,
            )
        )
    return FunctionalParse(path=path, chords=chords)


def build_functional_parse(harmonic_analysis: Sequence[dict]) -> dict:
    """Ponte para o `AnalysisService`: consome a análise determinística por acorde."""
    codes = [e.get("function_code", "Outro") for e in harmonic_analysis]
    symbols = [e.get("chord", "?") for e in harmonic_analysis]
    strengths = [e.get("strength") for e in harmonic_analysis]
    return parse_codes(codes, symbols, strengths).to_dict()


def parse_progression(
    symbols: Sequence[str], key: Optional[str] = None, mode: str = "major"
) -> FunctionalParse:
    """Parsing autônomo de uma progressão (offline, sem provider) — útil em testes."""
    chords = [Chord(s) for s in symbols]
    if key is None:
        est = detect_key([c.symbol for c in chords])
        if est:
            key, mode = est.key_note, est.mode
    analysis = HarmonicAnalysis(key, mode)
    codes: List[str] = []
    strengths: List[Optional[str]] = []
    for i, c in enumerate(chords):
        prev = chords[i - 1] if i > 0 else None
        nxt = chords[i + 1] if i < len(chords) - 1 else None
        codes.append(analysis.analyze_function(c, prev, nxt)[0])
        strengths.append(functional_strength(analysis.get_degree(c)))
    return parse_codes(codes, [c.symbol for c in chords], strengths)
