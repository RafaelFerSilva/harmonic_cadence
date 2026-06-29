"""Corpus curado de **centros modais** — o Caminho 2 da bifurcação analítica.

A parte (A) (`modal-mode-naming`) *nomeia* o modo que o algoritmo consegue
detectar ("D mixolídio"). Esta parte (B) *anota* o que a cifra do Cifra Club não
codifica mas a autoridade documenta: o **centro modal** de Chediak (finalis +
modo grego), para as peças cujo centro genuinamente diverge da leitura tonal
(Arrastão → Lá dórico, p.125; Procissão → Dó mixolídio, p.126).

Regra de ouro: o centro modal é um **fato musicológico curado**, injetado na
exibição — NUNCA lido das cifras (a sonda provou que o finalis é irrecuperável
das cifras do CC: ver `PROBE-FINDINGS.md`). Por construção, nada aqui toca
`detect_key` nem entra em métrica de detecção.

Escopo (D4): só **divergência de centro** (offset ≠ 0). Divergências de
*nome de modo* (Upa Neguinho, Pra Não Dizer — centro já correto) ficam com a
parte (A); não entram neste corpus.

Fronteira de copyright: só FATOS (centro/modo/página/nota/intervalo) — nunca o
texto, as tabelas ou as cifras do livro.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

from cifra_core.slug import slugify

ChurchMode = Literal[
    "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"
]


@dataclass(frozen=True, slots=True, kw_only=True)
class Citation:
    """Citação obrigatória — sem ela o fato não existe (muro de copyright = fatos
    citados). Falha rápido na importação se malformada."""

    source: str  # "Almir Chediak, Harmonia & Improvisação"
    volume: int  # 1
    page: int  # 125

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Citation.source vazio: todo fato modal exige a obra.")
        if self.volume < 1:
            raise ValueError(f"Citation.volume inválido: {self.volume!r}")
        if self.page < 1:
            raise ValueError(f"Citation.page inválida: {self.page!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class ModalCenterFact:
    """Um centro modal curado, identificado por artista+música.

    `finalis_from_tonal` (D5): o intervalo, em semitons, do finalis de Chediak
    relativo ao **centro tonal detectado** sobre as cifras raspadas — curado lendo
    a análise funcional de Chediak no arranjo, NUNCA `chediak_pc − cc_key_pc`
    (subtração absoluta cross-fonte, que quebra quando Chediak e o CC estão em
    transposições diferentes). Transposição-seguro por construção.
    """

    artist: str
    song: str
    curated_center: str  # finalis na edição de Chediak (ex. "A")
    curated_mode: ChurchMode
    finalis_from_tonal: int  # D5: intervalo (semitons) finalis − centro tonal detectado
    citation: Citation  # ← obrigatória, SEM default
    note: str = ""  # divergência de arranjo (pode ser vazia)

    def __post_init__(self) -> None:
        if not (0 <= self.finalis_from_tonal < 12):
            raise ValueError(
                f"finalis_from_tonal fora de 0..11: {self.finalis_from_tonal!r}"
            )

    @property
    def key(self) -> str:
        """Chave de identidade `slug(artista)|slug(música)` (reusa `cifra_core`)."""
        return f"{slugify(self.artist)}|{slugify(self.song)}"


CORPUS: tuple[ModalCenterFact, ...] = (
    ModalCenterFact(
        artist="Edu Lobo",
        song="Arrastao",
        curated_center="A",
        curated_mode="dorian",
        finalis_from_tonal=7,  # Lá (finalis) está uma 5ªJ acima do Ré tonal detectado
        citation=Citation(
            source="Almir Chediak, Harmonia & Improvisação", volume=1, page=125
        ),
        note=(
            "Concebida em Lá dórico; o arranjo do Cifra Club transpõe e omite o "
            "sinal funcional do dórico, então a leitura tonal reflete o arranjo "
            "(eixo Ré), não a concepção original."
        ),
    ),
    ModalCenterFact(
        artist="Gilberto Gil",
        song="Procissao",
        curated_center="C",
        curated_mode="mixolydian",
        finalis_from_tonal=3,  # Dó (finalis) está 3 semitons acima do Lá tonal detectado
        citation=Citation(
            source="Almir Chediak, Harmonia & Improvisação", volume=1, page=126
        ),
        note=(
            "Concebida em Dó mixolídio; no arranjo do Cifra Club o Dó mal aparece "
            "(a peça oscila entre Ré e Lá), então a leitura tonal reflete o arranjo, "
            "não a concepção original."
        ),
    ),
)


_INDEX: dict[str, ModalCenterFact] = {f.key: f for f in CORPUS}


def lookup_modal_center(artist: str, song: str) -> Optional[ModalCenterFact]:
    """Busca o fato de centro modal por identidade `slug(artista)|slug(música)`.

    Um *miss* retorna `None` (o caso comum — a esmagadora maioria das peças não
    tem centro modal divergente; sem nota, o relatório fica idêntico ao de hoje).
    """
    return _INDEX.get(f"{slugify(artist)}|{slugify(song)}")
