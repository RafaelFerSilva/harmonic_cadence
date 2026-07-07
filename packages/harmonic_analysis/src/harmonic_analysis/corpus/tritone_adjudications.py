"""Corpus curado de **vereditos de trítono** — fecha a malha neuro-simbólica.

O `v_ledger_tritone_nondominant` lista as ocorrências de trítono real que o coder
**não** leu como dominante (o resíduo `Emp` sobre dominantes-7 com `degree=?`). O
overlay ML *rankeia* a suspeita; este corpus registra o **veredito do Chediak** por
ocorrência, pela GEOMETRIA (raiz vs. tônica + resolução), não pelo rótulo — e devolve
o fato citado ao sistema (cruzado no ledger/report).

Regra de ouro: cada veredito é um **fato musicológico curado** com **citação
obrigatória** (sem página, o fato não existe). É camada de **anotação (PRATA)**:
NUNCA reescreve `function_code`/`degree` do coder. Um veredito que confirme defeito
real (ex.: `Ab7(#11)` que deveria ser SubV) motiva uma change de *fix downstream*
separada — precedente: a adjudicação de 2026-07-02 gerou `fix-tritone-t-by-degree`.

Escopo: só as ocorrências do ledger de trítono não-dominante. Identidade =
`slug(música)` + `position` (o mesmo par do ledger; múltiplas ocorrências por música).

Fronteira de copyright: só FATOS (veredito/página/nota/geometria), nunca o texto, as
tabelas ou as cifras do livro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from cifra_core.slug import slugify

# Reusa o gate de citação já testado (falha-rápido na importação).
from harmonic_analysis.corpus.modal_centers import Citation

# Enum fechado de veredito geométrico. Cada categoria cita uma página; o caso
# genuinamente indecidível é `ambiguous` (resíduo honesto DECLARADO, nunca forçado).
TritoneVerdictKind = Literal[
    "subv",  # SubV (tritone sub): raiz a trítono do alvo; assinatura #11 natural
    "chromatic_approach",  # aproximação cromática descendente a outro dominante
    "emp_legitimate",  # empréstimo modal genuíno (bVI7/bVII7 → repouso)
    "dsec_deceptive",  # secundário deceptivo (V7/x resolvendo fora do alvo)
    "ambiguous",  # indecidível pela geometria disponível (centro instável etc.)
]

_VALID_KINDS: frozenset[str] = frozenset(
    ("subv", "chromatic_approach", "emp_legitimate", "dsec_deceptive", "ambiguous")
)


@dataclass(frozen=True, slots=True, kw_only=True)
class TritoneVerdict:
    """Um veredito curado para UMA ocorrência do ledger de trítono.

    Identidade = `slug` + `position` (par do `v_ledger_tritone_nondominant`).
    `verdict` restrito ao enum fechado; `ambiguous` exige `note` (o porquê da
    indecisão). `citation` obrigatória para todo veredito não-ambíguo — sem página
    o fato não existe.
    """

    slug: str  # slug da música (chave do ledger)
    position: int  # posição da ocorrência (chave do ledger)
    symbol: str  # símbolo do acorde (redundante, p/ leitura humana)
    verdict: TritoneVerdictKind
    note: str  # geometria/justificativa (obrigatória p/ ambiguous)
    citation: Optional[Citation] = field(default=None)

    def __post_init__(self) -> None:
        if not self.slug.strip():
            raise ValueError("TritoneVerdict.slug vazio.")
        if self.position < 0:
            raise ValueError(f"TritoneVerdict.position inválida: {self.position!r}")
        if self.verdict not in _VALID_KINDS:
            raise ValueError(
                f"verdict fora do enum fechado: {self.verdict!r} "
                f"(válidos: {sorted(_VALID_KINDS)})"
            )
        if self.verdict == "ambiguous":
            if not self.note.strip():
                raise ValueError(
                    f"veredito 'ambiguous' ({self.slug} pos={self.position}) exige "
                    "nota com o porquê da indecisão — resíduo honesto é DECLARADO."
                )
        else:
            # Todo veredito decisivo cita Chediak — sem página, o fato não existe.
            if self.citation is None:
                raise ValueError(
                    f"veredito '{self.verdict}' ({self.slug} pos={self.position}) "
                    "sem citação: todo fato decisivo exige a obra + página."
                )

    @property
    def key(self) -> tuple[str, int]:
        """Chave de identidade `(slug, position)` — o par do ledger."""
        return (slugify(self.slug), self.position)


# ---------------------------------------------------------------------------
# Adjudicação (2026-07-07) do ledger residual n=293 (43 ocorrências, 20 músicas),
# todas `Emp` sobre dominantes-7. Geometria re-derivada do `corpus.duckdb`
# (centro funcional + raiz→grau + acorde-alvo). Método = TRITONE-ADJUDICATION.md
# (Chediak cap. XXXIV, pp.111-116): decide pela GEOMETRIA, não pelo rótulo.
#
# Postura CONSERVADORA (regra de ouro: nunca chute, Chediak é o árbitro):
# só recebe veredito DECISIVO o que a geometria força de modo incontestável e
# mapeia numa página JÁ estabelecida no repo. O resíduo bV7 (raiz a trítono do
# centro, deg=6) e os casos de centro instável ficam `ambiguous` com nota
# geométrica — o resíduo honesto DECLARADO, não forçado. Aguarda revisão do
# curador (autoridade Chediak) para promover ambíguos a decisivos com página.
#
# Citação da classe cromática: Chediak Vol. I, cap. XXXIV, p.111 — classifica os
# acordes de 7ª sem função dominante em três classes, incluindo "diatônicos
# cromaticamente alterados". Um dominante-7 um semitom ABAIXO do dominante real
# seguinte é aproximação cromática por essa classe (geometria incontestável).
# ---------------------------------------------------------------------------

_P111 = Citation(
    source="Almir Chediak, Harmonia & Improvisação", volume=1, page=111
)


def _amb(slug: str, position: int, symbol: str, note: str) -> TritoneVerdict:
    return TritoneVerdict(
        slug=slug, position=position, symbol=symbol, verdict="ambiguous", note=note
    )


def _chrom(slug: str, position: int, symbol: str, note: str) -> TritoneVerdict:
    return TritoneVerdict(
        slug=slug, position=position, symbol=symbol,
        verdict="chromatic_approach", note=note, citation=_P111,
    )


ADJUDICATIONS: tuple[TritoneVerdict, ...] = (
    # --- chromatic_approach (6): dom7 um semitom ABAIXO do dominante seguinte ---
    _chrom("demais", 39, "Eb7(9)",
           "Am: Eb7 um semitom abaixo de E7(b9) (V da tônica) — aproximação cromática."),
    _chrom("minha-namorada", 22, "Eb7(9)",
           "Am: Eb7 um semitom abaixo de E7(b9) (V da tônica) — aproximação cromática."),
    _chrom("minha-namorada", 41, "Eb7",
           "Am: Eb7 um semitom abaixo de E7(#5) (V da tônica) — aproximação cromática."),
    _chrom("minha-namorada", 65, "Eb7(9)",
           "Am: Eb7 um semitom abaixo de E7(b9) (V da tônica) — aproximação cromática."),
    _chrom("eh-menina", 15, "Ab7(9)",
           "Em: Ab7 um semitom abaixo de A7(9) (dominante seguinte) — aproximação cromática."),
    _chrom("aqui-o", 58, "Bb7(9/13)",
           "Em: Bb7 um semitom abaixo de B7(9/13) (V da tônica) — aproximação cromática."),
    # --- ambiguous (37): resíduo honesto (bV7 deg=6 / centro instável / resolução indecisa) ---
    _amb("amor-de-nada", 16, "Gb7",
         "Cm: Gb7 raiz a trítono do centro (bV7) → C7(9); resolve por trítono ao I. "
         "SubV/IV não confirmado / #IV blues? Sem página que decida."),
    _amb("ana-luiza", 33, "A7(b13)",
         "Ebm: A7 bV7 (trítono do centro) → Em7(b5); resolução não-canônica. Ambíguo."),
    _amb("ana-luiza", 35, "A7(b9/13)",
         "Ebm: A7 bV7 → A7(b9/b13) (repetição do próprio dominante). Ambíguo."),
    _amb("ana-luiza", 36, "A7(b9/b13)",
         "Ebm: A7 bV7 → A7(b9) (repetição). Ambíguo."),
    _amb("ana-luiza", 37, "A7(b9)",
         "Ebm: A7 bV7 → F7M (+8); resolução não-canônica. Ambíguo."),
    _amb("ana-luiza", 57, "A7(13)",
         "Ebm: A7 bV7 → Em7(b5) (+7). Ambíguo."),
    _amb("ana-luiza", 59, "A74(9)",
         "Ebm: A7sus bV7 → F#m7 (+9). Ambíguo."),
    _amb("aqui-o", 32, "Bb7(13)",
         "Em: Bb7 bV7 → Bb7(#5) (prolonga o próprio dominante). Ambíguo."),
    _amb("aqui-o", 33, "Bb7(#5)",
         "Em: Bb7(#5) bV7 → Gb7M(9) (+8). Ambíguo."),
    _amb("aqui-o", 51, "Bb7(#11)",
         "Em: Bb7(#11) bV7 → Bbm7(b5) (+0, mesma raiz). #11 sugere SubV mas a resolução "
         "não confirma. Ambíguo."),
    _amb("aqui-o", 60, "Bb7(9/13)",
         "Em: Bb7 bV7 → Abm7(9) (+10). Ambíguo."),
    _amb("ausencia-de-voce", 65, "B7(#11)",
         "Fm: B7(#11) bV7 → F7M por trítono (+6) ao I. #11 sugere SubV mas resolve por "
         "trítono, não por semitom. Ambíguo."),
    _amb("beatriz", 47, "A7(#11)",
         "Ebm: A7(#11) bV7 → A#m7(11) (+1, sobe um semitom). #11 sugere SubV, mas SubV "
         "resolve DESCENDO um semitom. Ambíguo."),
    _amb("bye-bye-brasil", 29, "Bb7(9)",
         "Dm: Bb7 raiz bVI (deg=8) → Em7 (ii); bVI7 (Subd. menor alterada, cf. p.113) mas "
         "em tom menor e sem resolução ao I. Ambíguo (candidato a emp_legitimate)."),
    _amb("bye-bye-brasil", 67, "Bb7(9)",
         "Dm: Bb7 bVI (deg=8) → Em7 (ii). Ambíguo (candidato a emp_legitimate)."),
    _amb("disa", 13, "Db7(9)",
         "Gm: Db7 bV7 (trítono do centro) → Eb7M (+2). Ambíguo."),
    _amb("disa", 30, "Db7(9)",
         "Gm: Db7 bV7 → Ab7(#11) (+7, outro dominante). Ambíguo."),
    _amb("embarcacao", 12, "A7(b5)",
         "Abm: A7(b5) raiz bII (deg=1) → A7 (prolonga). SubV/I? (bII7 resolve ao I por "
         "semitom, mas aqui prolonga). Ambíguo."),
    _amb("embarcacao", 13, "A7",
         "Abm: A7 bII (deg=1) → Cm6/Eb (+3). Ambíguo."),
    _amb("embarcacao", 38, "A7/E",
         "Abm: A7/E bII (deg=1) → Eb7M(9) por trítono (+6). Ambíguo."),
    _amb("flora", 27, "C#74(9)",
         "Centro tonal instável (None) — grau irrecuperável; resolução → C#7(9) (prolonga). "
         "Ambíguo por falta de centro."),
    _amb("flora", 28, "C#7(9)",
         "Centro None → C#7 → D7M(#5)/F# (+1, sobe um semitom a acorde de repouso). "
         "Ambíguo por falta de centro."),
    _amb("flora", 65, "C#74(9)",
         "Centro None → C#7sus (prolonga). Ambíguo por falta de centro."),
    _amb("flora", 66, "C#7(9)",
         "Centro None → C#7 → D7M(#5)/F# (+1). Ambíguo por falta de centro."),
    _amb("fotografia", 15, "F#7(13)",
         "Cm: F#7 bV7 (trítono) → C7M(9) por trítono (+6) ao I maior. bV7-substituto do I? "
         "Sem página que decida. Ambíguo."),
    _amb("gaiolas-abertas", 30, "A7(13)",
         "Ebm: A7 bV7 (trítono) → Ebm7(9) por trítono (+6) ao i. Ambíguo."),
    _amb("garota-de-ipanema", 14, "B7(9)",
         "Fm: B7 bV7 (trítono) → F#m7 (+7); resolução deceptiva. Candidato a dsec_deceptive "
         "mas sem alvo canônico confirmado. Ambíguo."),
    _amb("ilusao-a-toa", 24, "A7(13)",
         "C#m: A7 raiz bVI (deg=8) → Fm7 (+8). bVI7 (cf. p.113) sem resolução ao I. "
         "Ambíguo (candidato a emp_legitimate)."),
    _amb("imagem", 18, "C#7",
         "Gm: C#7 bV7 (trítono) → Am6/C (+8). Ambíguo."),
    _amb("o-amor-e-chama", 53, "Bb7(9)",
         "Em: Bb7 bV7 (trítono) → Em7(9) por trítono (+6) ao i. Ambíguo."),
    _amb("samba-de-uma-nota-so", 3, "Ab7(#11)",
         "Centro instável (None) — cadeia de dominantes da ponte; Ab7(#11) → Bm7 (+3). "
         "#11 sugere SubV, mas sem centro o grau é irrecuperável. Ambíguo."),
    _amb("samba-de-uma-nota-so", 7, "Ab7(#11)",
         "Centro None → Ab7(#11) → Dm7 por trítono (+6). Ambíguo por falta de centro."),
    _amb("samba-de-uma-nota-so", 25, "Ab7(#11)",
         "Centro None → Ab7(#11) → Bm7 (+3). Ambíguo por falta de centro."),
    _amb("samba-de-uma-nota-so", 29, "Ab7(#11)",
         "Centro None → Ab7(#11) → Bm7 (+3). Ambíguo por falta de centro."),
    _amb("samba-de-uma-nota-so", 33, "Ab7(#11)",
         "Centro None → Ab7(#11) → Dm7 por trítono (+6). Ambíguo por falta de centro."),
    _amb("samba-de-uma-nota-so", 42, "Ab7(#11)",
         "Centro None → Ab7(#11) → Bm7 (+3). Ambíguo por falta de centro."),
    _amb("sonho-de-maria", 36, "Db7(9)",
         "Gm: Db7 bV7 (trítono) → Fm7 (+4). Ambíguo."),
)


_INDEX: dict[tuple[str, int], TritoneVerdict] = {v.key: v for v in ADJUDICATIONS}


def lookup_tritone_verdict(slug: str, position: int) -> Optional[TritoneVerdict]:
    """Busca o veredito de uma ocorrência do ledger por `(slug, position)`.

    Um *miss* retorna `None` — a ocorrência ainda não foi adjudicada (nunca um
    veredito inventado).
    """
    return _INDEX.get((slugify(slug), position))
