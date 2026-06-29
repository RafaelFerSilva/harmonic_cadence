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

from harmonic_analysis.corpus import CORPUS, ModalCenterFact
from harmonic_analysis.domain.key_detection import (
    detect_key,
    dominant_regions,
    segment_keys,
)

Key = Tuple[int, str]  # (classe de altura da tônica, "major" | "minor")

# Offsets diatônicos de cada coleção (≈ armadura de clave), a partir da tônica.
MAJOR_OFFSETS = frozenset({0, 2, 4, 5, 7, 9, 11})  # T-T-S-T-T-T-S
MINOR_OFFSETS = frozenset({0, 2, 3, 5, 7, 8, 10})  # menor natural

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


def same_collection(gold: Key, detected: Key) -> bool:
    """True se a tônica detectada é um grau diatônico da escala do gold.

    Mede a **coleção** (≈ armadura de clave): o offset da tônica detectada
    dentro da escala do gold. Ignora deliberadamente o rótulo maior/menor do
    detectado, porque ele é não-confiável em peça modal — o K-S rotula "E menor"
    para uma peça em E frígio, cuja coleção real é a de C maior.
    """
    offsets = MAJOR_OFFSETS if gold[1] == "major" else MINOR_OFFSETS
    return (detected[0] - gold[0]) % 12 in offsets


@dataclass(frozen=True)
class KeyEval:
    name: str
    annotated: Key
    detected: Key
    mode_ok: bool
    exact: bool
    relative: bool
    same_collection: bool


def evaluate_song(
    name: str,
    chords: Iterable[str],
    annotated_key: str,
) -> Optional[KeyEval]:
    """Avalia uma música contra um tom anotado; None se faltar anotação ou detecção.

    Utilitário de comparação detectado×anotado (modo/exata/relativa/coleção). NÃO usa o
    Cifra Club como ouro de centro — o centro tonal é validado pelo critério FUNCIONAL do
    Chediak (`chediak_functional_center`) no baseline do songbook, não aqui."""
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
        same_collection=same_collection(annotated, detected),
    )


@dataclass(frozen=True)
class MultiKeyEval:
    """Avaliação de uma música modulante contra um gold multi-região.

    `primary_ok` (acerto parcial): a tônica primária foi detectada — pelo
    `detect_key` pontual ou como uma das regiões dominantes. `all_ok` (acerto
    total): TODAS as tonalidades do gold (primária + secundárias) aparecem entre
    as regiões dominantes. Fundamento: modulação por acorde pivô (Chediak p. 118).
    """

    name: str
    primary_gold: Key
    secondary_golds: Tuple[Key, ...]
    detected_key: Key
    detected_regions: Tuple[Key, ...]
    primary_ok: bool
    all_ok: bool


def evaluate_modulating_song(
    name: str,
    chords: Iterable[str],
    primary_gold: str,
    secondary_golds: Iterable[str],
) -> Optional[MultiKeyEval]:
    """Avalia uma música modulante; None se faltar gold primário ou detecção."""
    primary = parse_key(primary_gold)
    secondaries = tuple(
        k for g in secondary_golds if (k := parse_key(g)) is not None
    )
    syms = list(chords)
    est = detect_key(syms)
    if primary is None or est is None:
        return None
    detected: Key = (est.tonic_pc, est.mode)
    regions = dominant_regions(segment_keys(syms), len(syms))
    region_keys = tuple((r.estimate.tonic_pc, r.estimate.mode) for r in regions)
    region_set = set(region_keys)
    gold_keys = (primary, *secondaries)
    all_ok = all(g in region_set for g in gold_keys)
    primary_ok = detected == primary or primary in region_set
    return MultiKeyEval(
        name=name,
        primary_gold=primary,
        secondary_golds=secondaries,
        detected_key=detected,
        detected_regions=region_keys,
        primary_ok=primary_ok,
        all_ok=all_ok,
    )


def evaluate_corpus(
    songs: Iterable[Tuple[str, Iterable[str], str]],
) -> dict:
    """Métricas agregadas detectado×anotado sobre `(nome, acordes, tom_anotado)`.

    Utilitário de comparação (modo/exata/relativa/coleção) contra um tom anotado
    qualquer. NÃO é o baseline do projeto: o Cifra Club foi aposentado como ouro; a
    validação roda no `songbook_baseline` (centro funcional do Chediak + invariantes
    funcionais), invariante a transposição."""
    evals: List[KeyEval] = []
    for s in songs:
        e = evaluate_song(s[0], s[1], s[2])
        if e is not None:
            evals.append(e)
    n = len(evals)
    denom = n or 1
    return {
        "n": n,
        "mode_accuracy": sum(e.mode_ok for e in evals) / denom,
        "exact_accuracy": sum(e.exact for e in evals) / denom,
        "relative_aware_accuracy": sum(e.exact or e.relative for e in evals) / denom,
        "collection_accuracy": sum(e.same_collection for e in evals) / denom,
        "evals": evals,
    }


@dataclass(frozen=True)
class ModalCenterLedgerRow:
    """Uma linha do ledger de centro modal (NÃO é acurácia — nada é detectado).

    `detected_tonal_center` é o centro TONAL do `detect_key` sobre as cifras
    raspadas (pc, ou None se a detecção falhar). O finalis modal é dado pelo
    intervalo CURADO (`finalis_from_tonal`) — `implied_finalis_pc` é derivado
    SOMANDO esse intervalo ao centro detectado (anda junto com a transposição do
    arranjo), NUNCA por subtração absoluta cross-fonte."""

    artist: str
    song: str
    detected_tonal_center: Optional[int]
    curated_center: str
    curated_mode: str
    finalis_from_tonal: int
    page: int

    @property
    def implied_finalis_pc(self) -> Optional[int]:
        """Finalis no espaço de altura do ARRANJO (transposição-seguro): centro
        tonal detectado + intervalo curado. None se a detecção falhou."""
        if self.detected_tonal_center is None:
            return None
        return (self.detected_tonal_center + self.finalis_from_tonal) % 12


def modal_center_ledger(
    detected_centers: dict, corpus: Iterable[ModalCenterFact] = CORPUS
) -> List[ModalCenterLedgerRow]:
    """Cobertura + ledger de divergência sobre o conjunto curado (D6).

    NÃO é uma acurácia: nada é detectado — o centro modal é um fato citado. Cada
    linha quantifica o gap entre a leitura tonal (do arranjo) e a concepção de
    Chediak. `detected_centers` mapeia `fact.key` → centro tonal detectado (pc);
    uma chave ausente vira `None` (cobertura honesta, nunca superestimada).

    Transposição-seguro por construção: a linha carrega o intervalo CURADO
    (`finalis_from_tonal`), nunca `chediak_pc − cc_key_pc`.
    """
    rows: List[ModalCenterLedgerRow] = []
    for fact in corpus:
        rows.append(
            ModalCenterLedgerRow(
                artist=fact.artist,
                song=fact.song,
                detected_tonal_center=detected_centers.get(fact.key),
                curated_center=fact.curated_center,
                curated_mode=fact.curated_mode,
                finalis_from_tonal=fact.finalis_from_tonal,
                page=fact.citation.page,
            )
        )
    return rows


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
