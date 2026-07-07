"""Corpus curado de **vereditos de centro tonal** — fecha a malha da worklist #7.

A corroboração de centro (`detect_key` × `chediak_functional_center`) diverge em algumas
músicas (`center_status='diverge'`). Este corpus registra o **veredito do Chediak** por
música, pela GEOMETRIA da cadência visível (tônica repousa, V é tensão — Vol. I pp.84-85/87),
NUNCA pela anotação do Cifra Club, e devolve o fato citado ao sistema (view + report).

Achado do #7 (`WORKLIST-ADJUDICATION.md`): **não há regra-cega segura** — o `detect_key`
erra agarrando V/IV/ii/iii/relativa; o achador funcional erra agarrando um v/ii/pivô
tonicizado; há a **armadilha do ii-V** (nenhum pega a tônica, que é o alvo do V); e há
modulantes sem centro único. O enum de `winner` codifica exatamente isso.

Regra de ouro: cada veredito é um **fato musicológico curado** com **citação obrigatória**
(exceto `ambiguous`). É camada de **anotação (PRATA)**: NUNCA toca `detect_key`,
`chediak_functional_center`, `center_pc`/`center_status`. Um veredito que revele uma classe
que o detector erra de forma cirurgicamente corrigível motiva uma change de *fix downstream*
separada (precedente: `add-cadential-v-as-tonic-path`, Path C).

Distinto de `modal_centers` (que anota o CENTRO MODAL grego que a cifra não codifica —
Arrastão → Lá dórico); aqui é a divergência do centro TONAL entre dois métodos do motor.

Fronteira de copyright: só FATOS (centro/veredito/evidência/página); a evidência descreve a
cadência da PRÓPRIA música, nunca o texto/tabela/cifra do livro.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

from cifra_core.slug import slugify

# Reusa o gate de citação já testado (falha-rápido na importação).
from harmonic_analysis.corpus.modal_centers import Citation

Mode = Literal["major", "minor"]

# Enum fechado de vencedor. Codifica o achado do #7 (sem regra-cega): cada categoria
# nomeia COMO os métodos se relacionam com a tônica adjudicada.
CenterWinner = Literal[
    "detect",  # detect_key acertou; o funcional pegou um v/ii/pivô tonicizado
    "functional",  # o critério funcional acertou; o K-S pegou V/IV/ii/iii/relativa
    "neither_ii_v",  # armadilha ii-V: nenhum pegou a tônica (o alvo do V)
    "modulating",  # sem centro global único (o palpite pende pro fim)
    "ambiguous",  # indecidível pela cadência visível
]

_VALID_WINNERS: frozenset[str] = frozenset(
    ("detect", "functional", "neither_ii_v", "modulating", "ambiguous")
)
# Vereditos de centro único decisivo → exigem citação (o critério funcional aplicado).
_DECISIVE: frozenset[str] = frozenset(("detect", "functional", "neither_ii_v"))
_VALID_MODES: frozenset[str] = frozenset(("major", "minor"))


@dataclass(frozen=True, slots=True, kw_only=True)
class TonalCenterVerdict:
    """Um veredito curado para UMA música da worklist de centro.

    Identidade = `slug` (uma divergência por música). `curated_root`/`curated_mode` = o
    centro tonal adjudicado; `winner` restrito ao enum fechado; `evidence` = a cadência
    visível que decide. `citation` obrigatória para todo veredito não-`ambiguous`.
    """

    slug: str
    curated_root: str  # raiz do centro adjudicado (ex. "D", "C#")
    curated_mode: Mode
    winner: CenterWinner
    evidence: str  # a cadência visível que decide (da própria música)
    citation: Optional[Citation] = field(default=None)

    def __post_init__(self) -> None:
        if not self.slug.strip():
            raise ValueError("TonalCenterVerdict.slug vazio.")
        if not self.curated_root.strip():
            raise ValueError(f"curated_root vazio ({self.slug}).")
        if self.curated_mode not in _VALID_MODES:
            raise ValueError(f"curated_mode inválido: {self.curated_mode!r}")
        if self.winner not in _VALID_WINNERS:
            raise ValueError(
                f"winner fora do enum fechado: {self.winner!r} "
                f"(válidos: {sorted(_VALID_WINNERS)})"
            )
        if not self.evidence.strip():
            raise ValueError(
                f"veredito ({self.slug}) sem evidência: a cadência que decide é o 'porquê'."
            )
        # Citação obrigatória só p/ veredito de CENTRO ÚNICO decisivo; `modulating`/
        # `ambiguous` não têm centro único a citar (o resíduo honesto declara-se pela nota).
        if self.winner in _DECISIVE and self.citation is None:
            raise ValueError(
                f"veredito '{self.winner}' ({self.slug}) sem citação: todo fato decisivo "
                "exige a obra + página (o critério funcional, pp.84-85/87)."
            )

    @property
    def key(self) -> str:
        """Chave de identidade `slug(música)` (reusa `cifra_core`)."""
        return slugify(self.slug)


# ---------------------------------------------------------------------------
# Adjudicação (2026-07-07) da worklist de centro n=293 (46 divergências). Método =
# WORKLIST-ADJUDICATION.md (Chediak pp.84-85/87: tônica repousa, V é tensão), pela
# cadência VISÍVEL (âncora V→I; moldura 1º/último acorde), NUNCA pela anotação do CC.
# Onde a geometria corrente bate com a adjudicação prévia (n=170), o veredito é
# portado; onde o centro funcional deslocou (razao-de-viver funcional D→C) houve
# REEXAME. O indecidível (modo contestado; sem tônica única) é `ambiguous`/`modulating`
# DECLARADO, nunca forçado. Camada PRATA — não toca `detect_key`/`center_status`.
#
# Achado do #7 preservado: não há vencedor único (functional 28, detect 8, neither_ii_v
# 3, modulating 4, ambiguous 3). Um gate cirúrgico do detector (armadilha ii-V;
# V-como-tônica) é change de FIX DOWNSTREAM separada.
# ---------------------------------------------------------------------------

_P84 = Citation(
    source="Almir Chediak, Harmonia & Improvisação", volume=1, page=84
)


def _v(slug, root, mode, winner, evidence):
    return TonalCenterVerdict(
        slug=slug, curated_root=root, curated_mode=mode, winner=winner,
        evidence=evidence, citation=_P84,
    )


def _open(slug, root, mode, winner, evidence):  # modulating/ambiguous: sem citação
    return TonalCenterVerdict(
        slug=slug, curated_root=root, curated_mode=mode, winner=winner, evidence=evidence
    )


ADJUDICATIONS: tuple[TonalCenterVerdict, ...] = (
    # ── detect acertou; o funcional pegou v/ii/pivô/relativa tonicizado (8) ──────
    _v("eh-menina", "D", "major", "detect",
       "Fecha A7→D7M(9) (V-I a repouso maj7) + D7M(9) Em7 (I-ii); o funcional pegou o ii (Em)."),
    _v("enquanto-a-tristeza-nao-vem", "C", "minor", "detect",
       "Abertura i-iv-bVII-bIII-bVI-V; G7(b9)→Cm; o funcional pegou o v (Gm) tonicizado no fim."),
    _v("chora-tua-tristeza", "D", "major", "detect",
       "Abre D7M(9) D6 (tônica D nítida); o funcional pegou o G7M tonicizado no meio (ii-V→IV)."),
    _v("canto-de-ossanha", "C", "minor", "detect",
       "Vamp Cm Cm/Bb A° Ab6 abre/fecha; o funcional pegou o G7→C maior da ponte."),
    _v("imagem", "G", "minor", "detect",
       "Termina Gm7; D7(b9)→Gm (V→i); o funcional pegou um pivô G maior."),
    _v("nos-e-o-mar", "D", "major", "detect",
       "1º e último = D7M (moldura maior); o A7→Dm do meio é modulação passageira."),
    _v("tema-do-boneco-de-palha", "G", "minor", "detect",
       "Abre Gm7 Gm6; Am7(b5) D7(b9) Gm(7M) = ii-V-i; o funcional pegou a relativa maior (Bb)."),
    _v("feitinha-pro-poeta", "D", "major", "detect",
       "Fecha D6(9) (repouso maior); o funcional pegou o A7→Dm7 do corpo. Modo maior pelo repouso final."),
    # ── funcional acertou; o K-S pegou V/IV/ii/iii/relativa/paralela (28) ────────
    _v("ciume", "D", "major", "functional",
       "Em7 A7 D6/9 = ii-V-I; o detect pegou o II7 secundário (E7 = V/V)."),
    _v("bye-bye-brasil", "D", "minor", "functional",
       "Abre e fecha Dm7(9); A7(#11)→Dm7 (V→i); o detect pegou Em (2ªM acima)."),
    _v("desafinado", "F", "major", "functional",
       "Abre e fecha F6(9); C7(b9)→F6(9) (V→I); o detect pegou o G (ii/2ªM acima)."),
    _v("e-luxo-so", "D", "major", "functional",
       "Abre D7M; A7(9)→D7M (V→I); vamp fecha no A7 (o V); o detect pegou Em (ii)."),
    _v("ilusao-a-toa", "C#", "minor", "functional",
       "G#7(b13)→C#m7 (V→i); o detect pegou Eb (2ªM acima). Fecho em Db6(9) deixa o modo próximo do ambíguo."),
    _v("ligia", "C#", "minor", "functional",
       "Abre e volta a C#m7(9); G#7(b13)→C#m (V→i); o detect pegou uma área secundária (D#m)."),
    _v("menino-das-laranjas", "A", "minor", "functional",
       "Abre Am7; E7→Am7 (V→i); fecha no E7 (o V, vamp); o detect pegou Bm (2ªM acima)."),
    _v("por-causa-de-voce", "A", "major", "functional",
       "Abre A7M(9), fecha A6; E7(b9)→A6 (V→I); o detect pegou Bm (ii)."),
    _v("tereza-da-praia", "B", "major", "functional",
       "C#m7 F#7 B7M = ii-V-I (B7M/B6 repouso); o detect pegou o ii (C#m)."),
    _v("amor-em-paz", "F#", "major", "functional",
       "G7(#11) SubV→F#7M (SubV→I); o detect pegou Bm (região da 4ªJ). Fecho em F#m7 aproxima do paralelo."),
    _v("inutil-paisagem", "A", "major", "functional",
       "Abre A6, fecha A7M; a cadeia B7→E7→A7 pousa em A; o Dm é iv-cliché emprestado (o detect pegou o iv)."),
    _v("poema-azul", "G", "major", "functional",
       "1º=G7M(9), último=G; D7→G7M (V→I); o detect pegou o IV (C)."),
    _v("a-mulher-de-cada-porto", "D", "major", "functional",
       "Abre D6(9); A7(13)→D7M(9) (V→I); vamp fecha no A7 (o V); o detect pegou o V (A)."),
    _v("me-perdoe-maria", "D", "major", "functional",
       "Em7 A7 D6(9) = ii-V-I; o detect pegou o V (A)."),
    _v("razao-de-viver", "C", "major", "functional",
       "Fecha C7M; G7(9)→C7M(9) (V→I); o detect pegou o V (G). REEXAME: o centro funcional "
       "deslocou de Ré (n=170) para Dó (n=293) com a extração corrente."),
    _v("cancao-do-nosso-amor", "A", "major", "functional",
       "Bm7 E7 A / E7 A7M = ii-V-I a Lá; o detect pegou o iii (C#m)."),
    _v("cancao-que-morre-no-ar", "D", "major", "functional",
       "Fecha D7M; A7(9)→D7M (V→I); o detect pegou o iii (F#m)."),
    _v("samba-da-pergunta", "G", "major", "functional",
       "Abre e fecha G7M; D7(9)→G7M (V→I); o detect pegou o iii (Bm)."),
    _v("bloco-do-eu-sozinho", "F", "major", "functional",
       "C7(b9)→F7M (V→I); o detect pegou Am (iii/vi)."),
    _v("tempo-de-solidao", "D", "minor", "functional",
       "Fecha Dm7; A7(b9)→D (V→i); o detect pegou a relativa maior (F). A7→D7M sugere maior; adoto o repouso final Dm7."),
    _v("atras-da-porta", "F#", "minor", "functional",
       "Abre F#m7; C#7(b9)→F#m(7M) (V→i); o detect trocou o modo p/ maior."),
    _v("entrudo", "F", "minor", "functional",
       "C7(b9)→Fm7(9) (V→i); abre Cm7 (v); o detect trocou o modo p/ maior."),
    _v("eu-vim-da-bahia", "A", "minor", "functional",
       "Fecha Am7; Bb7(#11) SubV→Am7; o detect trocou o modo p/ maior."),
    _v("no-cordao-da-saideira", "E", "minor", "functional",
       "Em(add9) abre/fecha; B7(b9)→Em (V→i); o detect trocou o modo p/ maior."),
    _v("o-morro-nao-tem-vez", "A", "minor", "functional",
       "E7→Am7 (V→i); a vamp A7(13) G7(13) é bVII-I modal, não tônica maior; o detect trocou o modo."),
    _v("tema-de-amor-por-gabriela", "A", "major", "functional",
       "Fecha A7M(#11); Bb7(#11) SubV→A; o detect trocou o modo p/ menor."),
    _v("tudo-se-transformou", "E", "minor", "functional",
       "Abre e fecha Em7; B7→Em7 (V→i); o detect trocou o modo p/ maior."),
    _v("esperanca-perdida", "F", "major", "functional",
       "Abre F7M, fecha F6; Gb7(#11) SubV→F7M (SubV→I); o detect pegou a relativa menor (Dm)."),
    # ── armadilha do ii-V: nenhum pegou a tônica (o alvo do V) (3) ───────────────
    _v("bolinha-de-sabao", "C", "major", "neither_ii_v",
       "Dm7 G7 → C9/C7M = ii-V-I; o detect pegou o V (G7), o funcional o ii (Dm7); o I (C) é a tônica."),
    _v("menina", "C", "major", "neither_ii_v",
       "Dm7 G7 C7M = ii-V-I; o detect pegou o V (G7), o funcional o ii (Dm7); o I (C) é a tônica."),
    _v("rio", "F", "major", "neither_ii_v",
       "Gm7 C7 → F7M = ii-V-I; o detect pegou o V (C7), o funcional o ii (Gm7); o I (F) é a tônica."),
    # ── modulantes: sem tônica global única (o palpite pende pro fim) (4) ─────────
    _open("embarcacao", "D#", "major", "modulating",
          "84 acordes; a 2ª metade é a 1ª transposta ½t acima; sem tônica única (palpite: fim em D#)."),
    _open("ah-se-eu-pudesse", "E", "major", "modulating",
          "Abre em Eb maior; F7(#11) SubV→E7M fecha em E; modula, sem tônica global única."),
    _open("eu-te-amo", "B", "major", "modulating",
          "Descida cromática por muitas tonalidades; fecha C7(SubV)→B7M; sem tônica global única."),
    _open("maria-ninguem", "F", "major", "modulating",
          "Círculo A/C/F; C7(13)→F7M fecha em F, mas o corpo modula; baixa confiança."),
    # ── ambíguos: cadência visível não decide (modo/relativa/modal) (3) ──────────
    _open("ponteio", "E", "minor", "ambiguous",
          "Abre Em(7M/9) (menor); F7(#11) SubV→E6(9) (maior); peça modal (E), o modo não fecha."),
    _open("cartao-de-visita", "D", "major", "ambiguous",
          "Em7 A7 D9 recorre (ii-V a D), mas F#7→Bm7 também; relativa D/Bm genuína."),
    _open("eu-e-a-brisa", "E", "major", "ambiguous",
          "Abre E6(9) (repouso E maior), mas o funcional achou G#m (iii tonicizado) e a peça fecha em G#7M (III) — sem repouso único."),
)


_INDEX: dict[str, TonalCenterVerdict] = {v.key: v for v in ADJUDICATIONS}


def lookup_center_verdict(slug: str) -> Optional[TonalCenterVerdict]:
    """Busca o veredito de centro de uma música por slug. Miss → `None`."""
    return _INDEX.get(slugify(slug))
