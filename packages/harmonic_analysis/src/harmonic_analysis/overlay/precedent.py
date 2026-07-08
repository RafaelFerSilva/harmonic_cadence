"""Assistente de adjudicação por PRECEDENTE (case-based reasoning) — Camada C, Fase 1.

Para uma ocorrência suspeita (ledger de trítono não-dominante ou worklist de centro),
recupera os `k` casos **já adjudicados por humano** mais próximos pela GEOMETRIA
harmônica (função/grau/qualidade/intervalos — features de FUNÇÃO/INTERVALO, **nunca o
tom**) e emite um veredito **DRAFT** = o `verdict kind` + a `Citation` **herdados** do
precedente mais próximo, com a concordância dos `k` como confiança (denominador visível).

Leis (AGENTS.md / ML-EVOLUTION-PLAN §0):
- **PRATA**: só LÊ o banco + os corpora de adjudicação CONFIRMADOS; NUNCA reescreve
  `function_code`/`degree`, arbitra centro, ou toca gates/`detect_key`.
- **Draft nunca é adjudicação**: `status="draft"`; só o humano promove. A base de casos
  são SÓ vereditos confirmados (drafts nunca entram como precedente).
- **Fronteira de copyright**: a citação é SEMPRE herdada do precedente confirmado (fato
  já curado) — nunca extraída do texto/PDF do Chediak.
- **Avaliação descritiva**: a métrica é a taxa de confirmação humana (leave-one-out
  sobre os vereditos humanos), NUNCA acurácia contra o coder.

Por que CBR e não classificador: 89 labels desbalanceados → um classificador decora
(ML-EVOLUTION §5). O k-NN sobre geometria não treina parâmetro: usa o veredito humano
diretamente, é interpretável (aponta o precedente + citação) e degrada honesto (vizinho
`ambiguous` → draft `ambiguous`). Embeddings de acorde aprendidos são NO-GO (quebram a
invariância de transposição — `PROBE-EMBEDDINGS-FINDINGS.md`); a geometria de FUNÇÃO é
invariante por construção.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Optional

from harmonic_analysis.corpus.tonal_center_adjudications import (
    ADJUDICATIONS as CENTER_ADJUDICATIONS,
)
from harmonic_analysis.corpus.tritone_adjudications import (
    ADJUDICATIONS as TRITONE_ADJUDICATIONS,
)

if TYPE_CHECKING:
    import duckdb

    from harmonic_analysis.corpus.modal_centers import Citation

Ledger = Literal["tritone", "center"]

# Ortografia → pitch-class (idêntico ao mapa da `v_ledger_tritone_nondominant`; a
# grafia é a do detector, transposição cancela na subtração raiz−tônica).
_PC_FROM_SPELLING: dict[str, int] = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}

# Distância a partir da qual o precedente mais próximo é longe demais p/ herdar veredito
# decisivo → o draft cai em `ambiguous` (conservador; calibrável no probe). 0.0 = idêntico.
_AMBIGUOUS_CUTOFF = 0.5

_NO_FEATURE = "∅"  # categoria "ausente", 1ª classe (grau nulo etc.)


# ── Geometria transposição-invariante ────────────────────────────────────────
# Um traço é ('cat', str) categórico OU ('cyc', int 0..11) cíclico (intervalo).
Feature = tuple[str, object]
Geometry = dict[str, Feature]


def feature_distance(a: Geometry, b: Geometry) -> float:
    """Distância de geometria em [0,1]: média sobre os traços PRESENTES nos dois.

    Categórico = 0/1 (igual/diferente). Cíclico = distância circular normalizada
    (min(d, 12−d)/6 ∈ [0,1]). Traço ausente num dos lados não é comparado (features
    opcionais como resolução do último acorde). Sem traço em comum → distância máxima.
    """
    keys = set(a) & set(b)
    if not keys:
        return 1.0
    total = 0.0
    for key in keys:
        kind_a, val_a = a[key]
        kind_b, val_b = b[key]
        if kind_a == "cat":
            total += 0.0 if val_a == val_b else 1.0
        else:  # 'cyc'
            d = abs(int(val_a) - int(val_b)) % 12
            total += min(d, 12 - d) / 6.0
    return total / len(keys)


def _tonic_pc(spelling: Optional[str]) -> Optional[int]:
    return _PC_FROM_SPELLING.get(spelling) if spelling else None


def tritone_geometry(
    conn: "duckdb.DuckDBPyConnection", song_id: int, position: int
) -> Geometry:
    """Geometria (por ocorrência) de um caso do ledger de trítono.

    Traços: função, grau, qualidade (categóricos, já invariantes) + intervalo
    raiz→tônica e intervalo de resolução ao próximo acorde (cíclicos). Falha visível
    se `(song_id, position)` não existir.
    """
    row = conn.execute(
        "SELECT o.function_code, o.degree, v.quality, v.root_pc, s.detected_key, "
        "       nv.root_pc "
        "FROM chord_occurrence o "
        "JOIN v_song_current s ON o.song_id = s.song_id "
        "JOIN chord_vocab v    ON o.symbol = v.symbol "
        "LEFT JOIN chord_occurrence nx "
        "       ON nx.song_id = o.song_id AND nx.position = o.position + 1 "
        "LEFT JOIN chord_vocab nv ON nx.symbol = nv.symbol "
        "WHERE o.song_id = ? AND o.position = ?",
        [song_id, position],
    ).fetchone()
    if row is None:
        raise ValueError(
            f"ocorrência (song_id={song_id}, position={position}) não está no corpus "
            "(run corrente) — nada a assistir."
        )
    function_code, degree, quality, root_pc, detected_key, next_root_pc = row
    geom: Geometry = {
        "function": ("cat", function_code or _NO_FEATURE),
        "degree": ("cat", degree or _NO_FEATURE),
        "quality": ("cat", quality or _NO_FEATURE),
    }
    tonic = _tonic_pc(detected_key)
    if tonic is not None and root_pc is not None:
        geom["root_to_tonic"] = ("cyc", (int(root_pc) - tonic) % 12)
    if next_root_pc is not None and root_pc is not None:
        geom["resolution"] = ("cyc", (int(next_root_pc) - int(root_pc)) % 12)
    return geom


def center_geometry(conn: "duckdb.DuckDBPyConnection", song_id: int) -> Geometry:
    """Geometria (por música) de um caso da worklist de centro.

    Traços: modo detectado, modo funcional (categóricos) + intervalo raiz(detect)→
    raiz(funcional) (cíclico) — a assinatura da divergência, invariante a tom. Falha
    visível se a música não existir.
    """
    row = conn.execute(
        "SELECT detected_key, detected_mode, center_pc, center_mode "
        "FROM v_song_current WHERE song_id = ?",
        [song_id],
    ).fetchone()
    if row is None:
        raise ValueError(f"música (song_id={song_id}) não está no corpus (run corrente).")
    detected_key, detected_mode, center_pc, center_mode = row
    geom: Geometry = {
        "detected_mode": ("cat", detected_mode or _NO_FEATURE),
        "center_mode": ("cat", center_mode or _NO_FEATURE),
    }
    detect_pc = _tonic_pc(detected_key)
    if detect_pc is not None and center_pc is not None:
        geom["detect_to_center"] = ("cyc", (int(center_pc) - detect_pc) % 12)
    return geom


# ── Base de casos (SÓ vereditos confirmados) ─────────────────────────────────
@dataclass(frozen=True, slots=True)
class PrecedentCase:
    """Um precedente = um veredito humano confirmado + sua geometria."""

    key: tuple  # (slug, position) p/ trítono; (slug,) p/ centro
    slug: str
    symbol: str  # símbolo (trítono) ou centro adjudicado (centro), p/ leitura humana
    verdict: str  # verdict kind (trítono) ou winner (centro)
    citation: Optional["Citation"]
    note: str  # nota/evidência do precedente
    geometry: Geometry


def _resolve(conn: "duckdb.DuckDBPyConnection", slug: str) -> Optional[int]:
    row = conn.execute(
        "SELECT song_id FROM v_song_current WHERE slug = ?", [slug]
    ).fetchone()
    return row[0] if row else None


def load_case_base(
    conn: "duckdb.DuckDBPyConnection", ledger: Ledger
) -> list[PrecedentCase]:
    """Carrega os precedentes CONFIRMADOS de um ledger (nunca drafts).

    Reusa os corpora tipados em código (`Citation` já curada) como fonte da verdade;
    a geometria é re-derivada do banco. Casos cujo slug não está no run corrente são
    pulados (falha silenciosa só aqui é aceitável: precedente fora do corpus não existe).
    """
    cases: list[PrecedentCase] = []
    if ledger == "tritone":
        for adj in TRITONE_ADJUDICATIONS:
            sid = _resolve(conn, adj.slug)
            if sid is None:
                continue
            cases.append(
                PrecedentCase(
                    key=(adj.slug, adj.position),
                    slug=adj.slug,
                    symbol=adj.symbol,
                    verdict=adj.verdict,
                    citation=adj.citation,
                    note=adj.note,
                    geometry=tritone_geometry(conn, sid, adj.position),
                )
            )
    else:  # center
        for adj in CENTER_ADJUDICATIONS:
            sid = _resolve(conn, adj.slug)
            if sid is None:
                continue
            cases.append(
                PrecedentCase(
                    key=(adj.slug,),
                    slug=adj.slug,
                    symbol=f"{adj.curated_root} {adj.curated_mode}",
                    verdict=adj.winner,
                    citation=adj.citation,
                    note=adj.evidence,
                    geometry=center_geometry(conn, sid),
                )
            )
    return cases


# ── Veredito DRAFT ───────────────────────────────────────────────────────────
@dataclass(frozen=True, slots=True)
class DraftVerdict:
    """Um veredito rascunhado por precedente. NÃO é adjudicação — o humano promove."""

    key: tuple
    ledger: Ledger
    verdict: str  # herdado do precedente mais próximo (ou 'ambiguous' se longe demais)
    citation: Optional["Citation"]  # herdada; None p/ ambiguous
    confidence: float  # fração dos k que concordam com o mais próximo
    denominator: int  # k efetivo (nº de precedentes considerados)
    nearest_distance: float
    neighbors: tuple[tuple[PrecedentCase, float], ...]  # (precedente, distância)
    status: str = "draft"

    @property
    def is_ambiguous(self) -> bool:
        return self.verdict == "ambiguous"


def draft_verdict(
    geometry: Geometry,
    case_base: list[PrecedentCase],
    *,
    ledger: Ledger,
    key: tuple,
    k: int = 5,
    cutoff: float = _AMBIGUOUS_CUTOFF,
) -> DraftVerdict:
    """Rascunha um veredito por k-NN sobre a geometria.

    Exclui o auto-precedente (mesma `key`). Herda veredito + citação do mais próximo;
    confiança = concordância dos `k`. Precedente mais próximo além do `cutoff` (ou vizinho
    mais próximo `ambiguous`) → draft `ambiguous`, sem citação (resíduo honesto DECLARADO).
    """
    ranked = sorted(
        ((c, feature_distance(geometry, c.geometry)) for c in case_base if c.key != key),
        key=lambda cd: (cd[1], cd[0].slug, cd[0].key),
    )
    if not ranked:
        return DraftVerdict(
            key=key, ledger=ledger, verdict="ambiguous", citation=None,
            confidence=0.0, denominator=0, nearest_distance=1.0, neighbors=(),
        )
    top = ranked[: max(1, k)]
    nearest_case, nearest_dist = top[0]
    if nearest_dist > cutoff or nearest_case.verdict == "ambiguous":
        # Sem precedente decisivo próximo: honestamente indeciso, sem citação.
        return DraftVerdict(
            key=key, ledger=ledger, verdict="ambiguous", citation=None,
            confidence=sum(1 for c, _ in top if c.verdict == "ambiguous") / len(top),
            denominator=len(top), nearest_distance=nearest_dist,
            neighbors=tuple(top),
        )
    agree = sum(1 for c, _ in top if c.verdict == nearest_case.verdict)
    return DraftVerdict(
        key=key, ledger=ledger, verdict=nearest_case.verdict,
        citation=nearest_case.citation, confidence=agree / len(top),
        denominator=len(top), nearest_distance=nearest_dist, neighbors=tuple(top),
    )


def assist_occurrence(
    conn: "duckdb.DuckDBPyConnection",
    ledger: Ledger,
    slug: str,
    position: Optional[int] = None,
    k: int = 5,
) -> DraftVerdict:
    """Rascunha o veredito de UMA suspeita. Se já adjudicada, é leave-one-out (a base
    exclui a própria ocorrência) — o modo de avaliação honesto vs. o veredito humano."""
    sid = _resolve(conn, slug)
    if sid is None:
        raise ValueError(f"música '{slug}' não está no corpus (run corrente).")
    if ledger == "tritone":
        if position is None:
            raise ValueError("ledger de trítono exige --occurrence <slug>:<position>.")
        geom = tritone_geometry(conn, sid, position)
        key: tuple = (slug, position)
    else:
        geom = center_geometry(conn, sid)
        key = (slug,)
    return draft_verdict(
        geom, load_case_base(conn, ledger), ledger=ledger, key=key, k=k
    )


def leave_one_out(
    conn: "duckdb.DuckDBPyConnection", ledger: Ledger, k: int = 5
) -> dict:
    """Avaliação descritiva: reproduz o CBR cada veredito humano quando ELE é escondido?

    Para cada precedente, rascunha excluindo-o e compara o draft ao veredito humano.
    Retorna a taxa de concordância (leave-one-out) — hold-out do curador, NUNCA acurácia
    contra o coder. Descritivo: mede o alcance do CBR, não valida o corpus.
    """
    base = load_case_base(conn, ledger)
    drafts: list[tuple[PrecedentCase, DraftVerdict]] = []
    agree = 0
    for case in base:
        d = draft_verdict(case.geometry, base, ledger=ledger, key=case.key, k=k)
        if d.verdict == case.verdict:
            agree += 1
        drafts.append((case, d))
    return {
        "ledger": ledger,
        "n": len(base),
        "agree": agree,
        "rate": agree / len(base) if base else 0.0,
        "k": k,
        "drafts": drafts,
    }


def ii_v_trap_candidates(conn: "duckdb.DuckDBPyConnection") -> list[dict]:
    """Ranking PRATA de candidatos à armadilha ii-V, além dos 3 conhecidos.

    Geometria da armadilha (`neither_ii_v`), pós-Path D: o `detect_key` já foi corrigido
    para o I e o achador funcional segue no ii → raiz(funcional) = raiz(detect)+2 e o
    centro funcional é MENOR (o ii). Descritivo: NÃO toca `detect_key` nem o placar.
    """
    rows = conn.execute(
        "SELECT slug, title, detected_key, detected_mode, center_pc, center_mode "
        "FROM v_song_current WHERE center_status = 'diverge'"
    ).fetchall()
    known = {"bolinha-de-sabao", "menina", "rio"}
    out: list[dict] = []
    for slug, title, detected_key, dmode, center_pc, center_mode in rows:
        detect_pc = _tonic_pc(detected_key)
        if detect_pc is None or center_pc is None:
            continue
        # funcional = ii de X (X+2, menor); detect = I (X, maior) → funcional−detect = 2.
        if (int(center_pc) - detect_pc) % 12 == 2 and center_mode == "minor" \
                and dmode == "major":
            out.append({
                "slug": slug, "title": title,
                "known": slug in known,
            })
    out.sort(key=lambda d: (not d["known"], d["slug"]))
    return out
