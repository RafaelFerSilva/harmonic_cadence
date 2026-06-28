"""Detecção de tonalidade por Krumhansl-Schmuckler a partir dos acordes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from cifra_core.theory import parse, realize, root_pitch_class
from cifra_core.theory.chord_parse import Category, Third

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
# TIE_BAND=0.10: recalibrado (era 0.06) para cobrir "Papel Marché" (João Bosco),
# onde o gap K-S entre A minor (correto pelo histograma) e C major (gold Cifra Club)
# era ~0.08-0.10 — C major não entrava na banda apesar de corrob=7.00 vs 0.00.
TIE_BAND = 0.10            # banda de quase-empate sobre o score K-S do topo
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


# --- Gate de qualidade (Fase B / 3b) — corrige o CENTRO escapando da TIE_BAND ----
# Discriminador funcional (Chediak): a TÔNICA é repouso (aparece como maj7/6/m7/tríade);
# o V é tensão (aparece como dominante-7, o trítono). Se o centro do K-S aparece
# EXCLUSIVAMENTE como dominante e resolve numa 5ª abaixo num acorde de REPOUSO, o K-S
# pegou o V — corrige-se p/ o alvo. Robusto a secundários (o sinal é a saúde do repouso
# da peça inteira, não notas isoladas) e a blues (lá nenhum acorde é repouso → aborta).


def _chord_infos(symbols: Sequence[str]):
    """(raiz_pc, baixo_pc, categoria) por acorde; None quando não parseia."""
    out = []
    for s in symbols:
        try:
            p = parse(s)
            cat = p.category() if callable(p.category) else p.category
            out.append((p.root.pitch_class, (p.bass or p.root).pitch_class, cat))
        except Exception:
            out.append(None)
    return out


def _x_mode(present, X: int) -> Optional[str]:
    """Modo de X pela qualidade ESTÁVEL dos acordes em X (maj/min), ou None se X
    nunca descansa (só dominante → não é repouso, não é tônica)."""
    stable = [c for (r, _b, c) in present if r == X and c in (Category.MAJOR, Category.MINOR)]
    if not stable:
        return None
    return "minor" if Category.MINOR in stable and Category.MAJOR not in stable else "major"


def _functional_dominant_resolves(infos, X: int) -> bool:
    """Um V7/SubV7 FUNCIONAL (trítono, `Category.DOMINANT`) resolve em X em posição
    estrutural/final (baixo seguinte assenta em X). Mesmo crivo do
    `verify_tonal_center` (Chediak p.84/87), replicado no domínio para não acoplar
    `key_detection` a `scripts/`."""
    dom = (X + 7) % 12   # V de X
    subv = (X + 1) % 12  # SubV (bII7) de X
    n = len(infos)
    for i in range(max(0, n - CADENCE_WINDOW), n - 1):
        cur, nxt = infos[i], infos[i + 1]
        if (
            cur is not None
            and nxt is not None
            and cur[2] is Category.DOMINANT
            and cur[0] in (dom, subv)
            and nxt[1] == X
        ):
            return True
    return False


def _exclusive_dominant_path(infos, present, ks_pc: int) -> Optional[Tuple[int, str]]:
    """Caminho A (restrito): Y aparece SÓ como dominante-7 e resolve uma 5ª abaixo
    num alvo X de repouso. Pega o caso Garota de Ipanema (C7→F)."""
    # (1) Se Y descansa alguma vez (acorde não-dominante), é tônica de fato.
    ks_cats = [c for (r, _b, c) in present if r == ks_pc]
    if not ks_cats or any(c is not Category.DOMINANT for c in ks_cats):
        return None
    X = (ks_pc - 7) % 12
    # (2/3) Algum Y7 resolve no alvo (baixo seguinte em X)?
    resolves = any(
        cur is not None
        and nxt is not None
        and cur[0] == ks_pc
        and cur[2] is Category.DOMINANT
        and nxt[1] == X
        for cur, nxt in zip(infos, infos[1:])
    )
    if not resolves:
        return None
    # (4) X tem que ser repouso (senão é blues I7→IV7 → aborta).
    mode = _x_mode(present, X)
    return (X, mode) if mode is not None else None


def _anchored_resolution_path(infos, present, ks_pc: int) -> Optional[Tuple[int, str]]:
    """Caminho B (ancorado por resolução): mesmo que Y descanse OCASIONALMENTE (o
    caminho A aborta), corrige Y→X=(Y−7) quando o sinal FUNCIONAL é limpo — um
    V7/SubV funcional resolve em X (estrutural), X é o repouso PREDOMINANTE, e X é
    âncora estrutural (1º ou último acorde). Pega o V-como-tônica residual da MPB
    (A Banda/Apesar/Menino do Rio), onde a tônica-real-V é reusada como acorde de
    passagem e por isso aparece como repouso vez ou outra. Validado por simulação
    no corpus: corrige 3, zero regressão das corretas."""
    X = (ks_pc - 7) % 12
    if X == ks_pc:
        return None
    # (1) V7/SubV funcional → X em posição estrutural/final.
    if not _functional_dominant_resolves(infos, X):
        return None
    # (2) X é o repouso PREDOMINANTE (maj/min > dominante na raiz X, e ≥ 2).
    cats_X = [c for (r, _b, c) in present if r == X]
    rest = sum(1 for c in cats_X if c in (Category.MAJOR, Category.MINOR))
    dom = sum(1 for c in cats_X if c is Category.DOMINANT)
    if not (rest > dom and rest >= 2):
        return None
    # (3) X é âncora estrutural: raiz do PRIMEIRO acorde parseável. Só o primeiro
    # (não o último): a peça estabelece a tônica na abertura (CORROB_FIRST), e o
    # último acorde engana — Esquinas (tônica Fá) FECHA na relativa Ré menor, e usar
    # o último faria o gate trocar o modo (regressão). Abrir em X é o sinal robusto.
    first_root = next((t[0] for t in infos if t is not None), None)
    if X != first_root:
        return None
    mode = _x_mode(present, X)
    return (X, mode) if mode is not None else None


def _tritone_gate(
    symbols: Sequence[str], ks_best: Tuple[int, str]
) -> Optional[Tuple[int, str]]:
    """Centro corrigido pelo gate de QUALIDADE, ou None — ultraconservador.

    Discriminador FUNCIONAL (Chediak): a tônica é repouso, o V é tensão. Dois
    caminhos, ambos corrigindo o centro K-S `Y` para `X = (Y−7) mod 12`:

    - **A (restrito):** `Y` aparece SÓ como dominante-7 e resolve numa 5ª abaixo num
      alvo X de repouso (Garota de Ipanema). Ver `_exclusive_dominant_path`.
    - **B (ancorado):** mesmo que `Y` descanse ocasionalmente, corrige quando um
      V7/SubV funcional resolve em X (estrutural), X é o repouso predominante e X é
      âncora (1º/último acorde) — o V-como-tônica residual da MPB. Ver
      `_anchored_resolution_path`.

    Guards (ambos os caminhos): blues sem repouso aborta (X também só dominante),
    dim7 inelegível (não é `Category.DOMINANT`), tônica que descansa não é rebaixada
    pelo A. Conservador: nas peças corretas nenhum caminho dispara."""
    infos = _chord_infos(symbols)
    present = [i for i in infos if i is not None]
    if not present:
        return None
    ks_pc = ks_best[0]
    a = _exclusive_dominant_path(infos, present, ks_pc)
    if a is not None:
        return a
    return _anchored_resolution_path(infos, present, ks_pc)


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

    # Gate de qualidade (3b): se o centro do K-S aparece só como dominante-7 e resolve
    # numa 5ª abaixo num acorde de repouso, o K-S confundiu o V com a tônica — corrige.
    # Ultraconservador (não toca peça cuja tônica descansa); blues aborta. Ver _tritone_gate.
    gated = _tritone_gate(symbols, (best_tonic, best_mode))
    if gated is not None and gated != (best_tonic, best_mode):
        best_tonic, best_mode = gated
        best_score = next(
            (s for s, t, m in ranked if (t, m) == (best_tonic, best_mode)),
            best_score,
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
    return KeyEstimate(
        best_tonic, best_mode, round(best_score, 4), name, key_note, alts
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


def _region_len(r: KeyRegion) -> int:
    return r.end - r.start + 1


def _same_key(a: KeyRegion, b: KeyRegion) -> bool:
    return (
        a.estimate.tonic_pc == b.estimate.tonic_pc
        and a.estimate.mode == b.estimate.mode
    )


def _coalesce(regions: List[KeyRegion]) -> List[KeyRegion]:
    """Funde regiões adjacentes de mesma tonalidade (tônica + modo iguais).

    A estimativa da região maior prevalece (mais confiável); o span resultante
    cobre ambas.
    """
    if not regions:
        return []
    merged = [regions[0]]
    for r in regions[1:]:
        prev = merged[-1]
        if _same_key(prev, r):
            keep = prev.estimate if _region_len(prev) >= _region_len(r) else r.estimate
            merged[-1] = KeyRegion(prev.start, r.end, keep)
        else:
            merged.append(r)
    return merged


def dominant_regions(
    regions: List[KeyRegion], n_chords: int, min_pct: float = 0.10
) -> List[KeyRegion]:
    """Pós-processa a saída de ``segment_keys`` em regiões dominantes legíveis.

    Funde fragmentos adjacentes de mesma tonalidade e, em seguida, absorve
    iterativamente cada região menor que ``min_pct`` dos acordes totais na vizinha
    de mesma tonalidade (se houver) ou, na falta dela, na vizinha de score K-S mais
    próximo. ``segment_keys`` NÃO é alterado — esta função só reduz a granularidade
    da apresentação (e habilita a métrica multi-região). A absorvente mantém sua
    própria estimativa (ela domina) e estende o span para cobrir a região pequena.
    """
    merged = _coalesce(list(regions))
    if len(merged) <= 1 or n_chords <= 0:
        return merged

    threshold = min_pct * n_chords
    while len(merged) > 1:
        idx = min(range(len(merged)), key=lambda i: _region_len(merged[i]))
        if _region_len(merged[idx]) >= threshold:
            break
        small = merged[idx]
        left = merged[idx - 1] if idx > 0 else None
        right = merged[idx + 1] if idx < len(merged) - 1 else None

        same_key = [nb for nb in (left, right) if nb and _same_key(nb, small)]
        if same_key:
            absorber = same_key[0]
        elif left and right:
            absorber = min(
                (left, right),
                key=lambda nb: abs(nb.estimate.score - small.estimate.score),
            )
        else:
            absorber = left or right  # região pequena numa das pontas

        new_region = KeyRegion(
            min(absorber.start, small.start),
            max(absorber.end, small.end),
            absorber.estimate,
        )
        kept = [r for r in merged if r is not small and r is not absorber]
        kept.append(new_region)
        kept.sort(key=lambda r: r.start)
        merged = _coalesce(kept)

    return merged
