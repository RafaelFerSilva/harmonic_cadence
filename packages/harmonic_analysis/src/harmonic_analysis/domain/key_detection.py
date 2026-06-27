"""Detecção de tonalidade por Krumhansl-Schmuckler a partir dos acordes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from cifra_core.theory import parse, realize, root_pitch_class
from cifra_core.theory.chord_parse import Third

from harmonic_analysis.domain.modal import detect_mode

# Perfis de tonalidade Krumhansl-Kessler.
KS_MAJOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
KS_MINOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

# Spellings convencionais de tonalidade por classe de altura.
MAJOR_NAMES = ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
MINOR_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"]

# Pesos calibrados no corpus de validação (test_key_corpus): 100% de acerto.
ROOT_WEIGHT = 2.0      # ênfase na fundamental de cada acorde
CADENCE_WEIGHT = 2.0   # ênfase no acorde final (resolução cadencial → tônica)

# --- Corroboração cadencial (Fase B) ---------------------------------------
# Desempata quase-empates do K-S (a confusão maior↔relativa-menor) usando o
# centro tonal funcional, que o histograma ignora. Fonte: Chediak (as cadências,
# XXXII pp. 109-111; o acorde final e a função do baixo como marcadores de tom).
# EPS conservador (banda de empate) e pesos num só lugar — recalibráveis contra o
# corpus, NÃO maximizados in-sample (ver design de tonal-center-detection).
TIE_BAND = 0.06            # banda de quase-empate sobre o score K-S do topo
CADENCE_WINDOW = 4         # nº de acordes finais inspecionados pela cadência
CORROB_FIRST = 1.0         # 1º acorde com fundamental == tônica
CORROB_LAST = 2.0          # último acorde com fundamental == tônica
CORROB_LAST_QUALITY = 1.0  # qualidade do último acorde casa (+) / contraria (−) o modo
CORROB_CADENCE = 3.0       # cadência autêntica dominante→tônica no fim (marcador forte)

# Correção de modo paralelo (mesma tônica, maior↔menor): a cadência não distingue
# (a dominante é comum), então o sinal é a qualidade dos acordes de tônica. Só age na
# tônica âncora (assenta/cadência) e exige um voto líquido decisivo — recalibrável.
PARALLEL_VOTE_THRESHOLD = 2  # net de acordes de tônica (menor − maior) p/ inverter


@dataclass(frozen=True)
class KeyEstimate:
    tonic_pc: int
    mode: str          # "major" | "minor"
    score: float
    name: str          # ex.: "C major"
    key_note: str      # ex.: "C" (para HarmonicAnalysis)
    alternatives: Tuple[Tuple[str, float], ...] = ()
    church_mode: Optional[str] = None  # modo de igreja quando aplicável


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


def cadence_corroboration(
    symbols: Sequence[str], tonic_pc: int, mode: str
) -> float:
    """Corroboração funcional de um centro tonal candidato — sinais que o
    histograma de pitch-classes descarta: o 1º acorde, o último acorde (e sua
    qualidade vs. o modo) e uma cadência autêntica (a dominante do candidato,
    ``tônica+7``, resolvendo na tônica) no fim.

    A âncora tonal é o **baixo**, não a fundamental (lição da Sina: ``D/A`` é Ré
    sobre pedal de Lá — o centro é Lá). Usa o baixo para "assenta na tônica" e
    para o alvo da cadência; a fundamental só identifica o acorde dominante (a
    identidade do V independe da inversão). Fonte: Chediak (cadências; baixo)."""
    roots: List[Optional[int]] = []
    basses: List[Optional[int]] = []
    quals: List[Optional[str]] = []
    for s in symbols:
        try:
            p = parse(s)
            roots.append(p.root.pitch_class)
            basses.append((p.bass or p.root).pitch_class)
            quals.append("minor" if p.third is Third.MINOR else "major")
        except Exception:
            roots.append(None)
            basses.append(None)
            quals.append(None)

    score = 0.0
    if basses and basses[0] == tonic_pc:
        score += CORROB_FIRST
    if basses and basses[-1] == tonic_pc:  # assenta na tônica (baixo)
        score += CORROB_LAST
        if roots[-1] == tonic_pc and quals[-1] is not None:  # tônica de fato (raiz)
            score += CORROB_LAST_QUALITY if quals[-1] == mode else -CORROB_LAST_QUALITY

    # Resolução de função dominante na tônica: a dominante (V, 5ª justa acima) OU
    # seu substituto tritonal (SubV / bII7, meio-tom acima) — ambos cadência
    # autêntica em MPB/bossa (Chediak). Identidade pela raiz; alvo pelo baixo.
    dom = (tonic_pc + 7) % 12
    subv = (tonic_pc + 1) % 12
    for i in range(max(0, len(roots) - CADENCE_WINDOW), len(roots) - 1):
        if roots[i] in (dom, subv) and basses[i + 1] == tonic_pc:
            score += CORROB_CADENCE
            break
    return score


def _correct_parallel_mode(
    symbols: Sequence[str], tonic_pc: int, mode: str
) -> str:
    """Corrige a confusão de modo PARALELO (mesma tônica, maior↔menor), que a
    cadência não distingue (a dominante é comum a ambas). Só age se a tônica é a
    **âncora tonal** (último baixo == tônica, ou cadência autêntica V/SubV → tônica)
    e a **qualidade dos acordes de tônica** contradiz o modo do K-S com força. O
    gate de âncora-baixo impede inverter o modo de uma tônica impostora (confusão
    relativa). Fonte: Chediak (a 3ª da tônica define o modo)."""
    roots: List[Optional[int]] = []
    basses: List[Optional[int]] = []
    quals: List[Optional[str]] = []
    for s in symbols:
        try:
            p = parse(s)
            roots.append(p.root.pitch_class)
            basses.append((p.bass or p.root).pitch_class)
            quals.append("minor" if p.third is Third.MINOR else "major")
        except Exception:
            roots.append(None)
            basses.append(None)
            quals.append(None)

    # Gate: a tônica detectada é a âncora tonal?
    anchored = bool(basses) and basses[-1] == tonic_pc
    if not anchored:
        dom, subv = (tonic_pc + 7) % 12, (tonic_pc + 1) % 12
        for i in range(max(0, len(roots) - CADENCE_WINDOW), len(roots) - 1):
            if roots[i] in (dom, subv) and basses[i + 1] == tonic_pc:
                anchored = True
                break
    if not anchored:
        return mode

    vote = sum(
        (1 if q == "minor" else -1)
        for r, q in zip(roots, quals)
        if r == tonic_pc and q is not None
    )
    if mode == "major" and vote >= PARALLEL_VOTE_THRESHOLD:
        return "minor"
    if mode == "minor" and vote <= -PARALLEL_VOTE_THRESHOLD:
        return "major"
    return mode


def detect_key(symbols: Sequence[str]) -> Optional[KeyEstimate]:
    """Estima a tonalidade correlacionando o perfil com os 24 perfis K-S; no
    quase-empate desempata pela corroboração cadencial (tom), e corrige a confusão
    de modo paralelo na tônica âncora (modo)."""
    profile = pitch_class_profile(symbols)
    if sum(profile) == 0:
        return None

    ranked: List[Tuple[float, int, str]] = []
    for tonic in range(12):
        rotated = [profile[(tonic + i) % 12] for i in range(12)]
        ranked.append((_pearson(rotated, KS_MAJOR), tonic, "major"))
        ranked.append((_pearson(rotated, KS_MINOR), tonic, "minor"))
    ranked.sort(key=lambda t: t[0], reverse=True)

    # Desempate cadencial: SÓ entre candidatos em quase-empate (banda TIE_BAND do
    # topo) escolhe o que o centro tonal funcional corrobora; tie-break pelo score
    # K-S, então um K-S confiante (fora da banda) nunca é sobreposto.
    top_score = ranked[0][0]
    band = [r for r in ranked if r[0] >= top_score - TIE_BAND]
    best_score, best_tonic, best_mode = max(
        band, key=lambda r: (cadence_corroboration(symbols, r[1], r[2]), r[0])
    )

    # Correção de modo paralelo (mesma tônica, maior↔menor) — após escolher o tom.
    corrected = _correct_parallel_mode(symbols, best_tonic, best_mode)
    if corrected != best_mode:
        best_mode = corrected
        best_score = next(
            s for s, t, m in ranked if (t, m) == (best_tonic, best_mode)
        )

    name, key_note = _name(best_tonic, best_mode)
    alts = tuple(
        (f"{_name(t, m)[0]}", round(s, 4))
        for s, t, m in ranked
        if (t, m) != (best_tonic, best_mode)
    )[:3]
    info = detect_mode(symbols)
    church_mode = info.mode if info else None
    return KeyEstimate(
        best_tonic, best_mode, round(best_score, 4), name, key_note, alts, church_mode
    )


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
