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
# Citação da classe cromática: Chediak Vol. I, cap. XXXIV **c) "Acordes diatônicos
# cromaticamente alterados", p.116** — acordes de ESTRUTURA de sétima da dominante
# SEM função dominante, com movimento do baixo por grau conjunto e SEM resolução
# dominante (estrutura constante). Um dominante-7 um semitom ABAIXO do V real,
# resolvendo para CIMA nele, é dessa classe (nunca SubV, que resolve para baixo).
# ADJUDICAÇÃO HUMANA COMPLETA (2026-07-07) — ledger de trítono 100% revisado pelo
# curador contra o texto do Vol. I pp.111-116, caso a caso:
#   • 6 `chromatic_approach` CONFIRMADAS → Chediak XXXIV c, p.116 (citação afiada de
#     p.111→p.116, a categoria específica "cromaticamente alterados").
#   • bVI7 (bye-bye-brasil ×2, ilusao-a-toa) REFUTADAS → o quadro p.113 é empréstimo em
#     MAIOR resolvendo no I; aqui é tom menor + resolve no ii/cromático. Ficam ambiguous.
#   • #11 (beatriz, ausencia, aqui-o/51, samba ×6) REFUTADAS → #11≠SubV (SubV resolve ½t
#     ABAIXO, p.114); resolvem p/ cima / trítono / mesma-raiz / centro=None. Ficam ambiguous.
#   • resíduo bV7/#IV7 (25 casos, deg=6 salvo flora=None e embarcacao=bII modulante)
#     CONFIRMADO indecidível — não é SubV/c)/bVI7; classe "Emp genérico sem página que
#     decida", consistente com TRITONE-ADJUDICATION.md (n=170). Ficam ambiguous honestos.
#   • FLAG p/ FIX DOWNSTREAM (não veredito): disa/30 (Db7→Ab7 por 4ªJ) pode ser Dext
#     mis-codado Emp — revisar no coder, não aqui.
# Resultado: 6 decididas citadas + 37 ambiguous honestas (nenhuma forçada). PRATA intacto.
# ---------------------------------------------------------------------------

_P116 = Citation(
    source="Almir Chediak, Harmonia & Improvisação", volume=1, page=116
)


def _amb(slug: str, position: int, symbol: str, note: str) -> TritoneVerdict:
    return TritoneVerdict(
        slug=slug, position=position, symbol=symbol, verdict="ambiguous", note=note
    )


def _chrom(slug: str, position: int, symbol: str, note: str) -> TritoneVerdict:
    return TritoneVerdict(
        slug=slug, position=position, symbol=symbol,
        verdict="chromatic_approach", note=note, citation=_P116,
    )


ADJUDICATIONS: tuple[TritoneVerdict, ...] = (
    # --- chromatic_approach (6): estrutura de dom7 SEM função dominante, baixo por
    # grau conjunto, resolvendo para CIMA no V (Chediak XXXIV c, p.116). HUMANO. ---
    _chrom("demais", 39, "Eb7(9)",
           "Am: …B7 B7 Eb7→E7(b9)→Am; baixo B→Eb→E; cromático subindo ao V (XXXIV c)."),
    _chrom("minha-namorada", 22, "Eb7(9)",
           "A: D/F# F7 Eb7→E7(b9); baixo F#→F→Eb→E, estrutura constante descendente (XXXIV c)."),
    _chrom("minha-namorada", 41, "Eb7",
           "A: Bb7M Eb7→E7(#5)→A7M; baixo Bb→Eb→E→A; cromático ao V (XXXIV c)."),
    _chrom("minha-namorada", 65, "Eb7(9)",
           "A: D/F# F7 Eb7→E7(b9); baixo F#→F→Eb→E, estrutura constante (XXXIV c) — igual pos22."),
    _chrom("eh-menina", 15, "Ab7(9)",
           "D: Bm7 Bb7 Ab7→A7sus→D7M; baixo B→Bb→Ab→A, descendente constante ao V (XXXIV c)."),
    _chrom("aqui-o", 58, "Bb7(9/13)",
           "E: Bb7↔B7↔Bb7; bordadura cromática do V (B7), estrutura constante (XXXIV c)."),
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
         "E: Bm7 Bb7(#11) → Bbm7(b5) Eb7→Ab; bV7. HUMANO (2026-07-07): #11≠SubV (SubV "
         "resolve ½t ABAIXO, p.114) — aqui troca de qualidade na MESMA raiz (Bb7→Bbm7b5), "
         "sem resolução. Resíduo bV7 honesto."),
    _amb("aqui-o", 60, "Bb7(9/13)",
         "Em: Bb7 bV7 → Abm7(9) (+10). Ambíguo."),
    _amb("ausencia-de-voce", 65, "B7(#11)",
         "Fm: Gb6 B7(#11) → F7M; bV7 (trítono). HUMANO (2026-07-07): #11≠SubV (SubV resolve "
         "½t abaixo, p.114) — aqui resolve por TRÍTONO à tônica (F). Resíduo bV7 honesto."),
    _amb("beatriz", 47, "A7(#11)",
         "Eb maj: B7M(9) A7(#11) → A#m7(=Bbm7, a v); bV7. HUMANO (2026-07-07): #11≠SubV "
         "(SubV resolve ½t ABAIXO, p.114) — aqui sobe ½t a um acorde MENOR (Bbm7), não "
         "dominante; não é c) (não é estrutura constante). Resíduo bV7 honesto."),
    _amb("bye-bye-brasil", 29, "Bb7(9)",
         "Dm: F7M Bb7(9)→Em7(ii); Bb7 deg=8. HUMANO (2026-07-07): NÃO é emp_legitimate — o "
         "bVI7-subd.menor-alt. da p.113 é empréstimo em MAIOR resolvendo no I; aqui é tom MENOR "
         "e resolve no ii (por trítono), + música `diverge` (centro instável). Ambíguo honesto."),
    _amb("bye-bye-brasil", 67, "Bb7(9)",
         "Dm: idem pos29 — Bb7 deg=8 → Em7(ii). HUMANO: não promove (menor + resolve no ii, "
         "fora do padrão bVI7→I da p.113). Ambíguo honesto."),
    _amb("disa", 13, "Db7(9)",
         "Gm: Db7 bV7 (trítono do centro) → Eb7M (+2). Ambíguo."),
    _amb("disa", 30, "Db7(9)",
         "Gm: Db7 → Ab7 por 4ªJ descendente (outro dominante). HUMANO (2026-07-07): "
         "assinatura de dominante ESTENDIDO (Dext, XXVIII pp.107-108), não Emp — se for, "
         "o coder codar Emp é DEFEITO → candidato a FIX DOWNSTREAM (não cadeia clara isolada, "
         "então fica flag de revisão de coder, não veredito). Ambíguo aqui."),
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
         "C#m: E7 A74 A7(13)→Fm7; A7 deg=8. HUMANO (2026-07-07): NÃO é emp_legitimate — o A7 é "
         "TONICIZADO por E7 (E7→A = V→I secundário), não um bVI7 emprestado; e vai a Fm7 "
         "(cromático), não ao I. Fora do padrão p.113. Ambíguo honesto."),
    _amb("imagem", 18, "C#7",
         "Gm: C#7 bV7 (trítono) → Am6/C (+8). Ambíguo."),
    _amb("o-amor-e-chama", 53, "Bb7(9)",
         "Em: Bb7 bV7 (trítono) → Em7(9) por trítono (+6) ao i. Ambíguo."),
    _amb("samba-de-uma-nota-so", 3, "Ab7(#11)",
         "Ponte cromática descendente (Bm7 Bb7 Am7 Ab7…), centro=None. HUMANO (2026-07-07): "
         "#11≠SubV (p.114); estrutura MISTA (m7/dom7), não é planagem constante pura da "
         "categoria c); + centro=None → grau irrecuperável. Ambíguo por falta de centro."),
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
