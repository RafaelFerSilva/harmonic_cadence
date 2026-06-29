"""Ground-truth ESTRUTURAL de centro tonal — ancorado em Chediak (árbitro).

Mede o **centro** (qual grau é a tônica), distinto da tônica-exata absoluta do
`key_baseline`. Blindado contra a anotação ingênua do Cifra Club por **proveniência**:

- `chediak`   — centro do livro, página citada (autoridade; âncora de validação
                NÃO-circular da change 2 do gate do trítono).
- `verified`  — centro confirmado por critério MECÂNICO ao vivo (`verify_tonal_center`):
                um V7/SubV7 FUNCIONAL (trítono real, Chediak p.84/87) resolvendo no tom
                do Cifra Club em posição estrutural/final → o cc_key É a tônica.
- `unverified`— nem A nem B → QUARENTENA, fora do `center_accuracy`.

O `cc_key` (tom do Cifra Club, `Cifra.key`) é só **âncora de transposição**, nunca a
fonte da verdade do centro. O `structural_offset` é derivado AO VIVO de
`(centro_Chediak − cc_key) % 12` — não é hard-coded. Muro de copyright: só FATOS
(música→centro→modo→página); NUNCA as harmonizações/cifras/tabelas da Parte 4.
"""

from typing import List, Optional, Sequence, Tuple

from cifra_core.theory import Note
from cifra_core.theory.chord_parse import parse
from harmonic_analysis.corpus import CORPUS


def _category(p) -> str:
    c = p.category
    return (c() if callable(c) else c).value


# --- TIER A: fatos de centro do Chediak (Parte 2, pp.121-127) -----------------
# (artista, música, centro_Chediak, modo, página, nota). Fatos citados, RESERVADOS.
# As entradas de **divergência de centro** (offset ≠ 0: Arrastão, Procissão) são a
# ÚNICA FONTE no corpus curado `harmonic_analysis.corpus.modal_centers.CORPUS` — não
# duplicamos aqui (honra "uma fonte"). As de **nome de modo só** (Upa, Pra Não Dizer:
# centro já correto) ficam com a parte (A) (`modal-mode-naming`), fora do CORPUS (D4),
# então seguem literais. A derivação de offset por subtração absoluta
# `(centro_Chediak − cc_key)` só vale na MESMA transposição — falsa em "Pra Não Dizer"
# (Chediak Mi, CC Fá): o CORPUS usa `finalis_from_tonal` (intervalo curado), não altura.
TIER_A_CHEDIAK = [
    *(
        (f.artist, f.song, f.curated_center, f.curated_mode, f.citation.page, f.note)
        for f in CORPUS
    ),
    ("Edu Lobo", "Upa Neguinho", "D", "mixolydian", 126,
     "Ré mixolídio (centro = Ré; só o modo diverge do tonal)"),
    ("Geraldo Vandre", "Pra Nao Dizer Que Nao Falei das Flores", "E", "aeolian", 127,
     "Mi eólio = menor natural; centro = Mi"),
]


# --- TIER C: centros TONAIS citados do Chediak (Parte 4, "Tom de X maior/menor") ---
# (artista, música, tom_Chediak, structural_offset, página, justificativa). Âncora de
# centro NÃO-circular (independe de dominante), expande o center_accuracy além das 19
# verificadas e revela buracos onde o detect_key discorda do livro.
#
# CRUX (degree-relative, NUNCA `tom_Chediak − cc_key` absoluto): o offset é o PAPEL da
# tônica de Chediak relativo à anotação do Cifra Club, invariante a transposição —
#   mesma tônica / mesmo papel (qualquer transposição)        → 0
#   CC anotou a RELATIVA maior da tônica menor de Chediak       → 9  (= −3)
#   CC anotou a RELATIVA menor da tônica maior de Chediak       → 3
# Curado lendo o "Tom de X" do livro + o papel do cc_key, JAMAIS do detect_key (sem
# circularidade). Só FATOS citados; nunca as harmonizações/cifras da Parte 4. Ver HARVEST.
TIER_C_TONAL = [
    ("Joao Bosco", "Papel Marche", "C", 0, 227,
     "Tom de Dó maior; cc_key C = mesma tônica → Chediak confirma o centro (não-circular)"),
    ("Milton Nascimento", "Coracao de Estudante", "F", 0, 232,
     "Tom de Fá maior; cc_key F = mesma tônica"),
    ("Chico Buarque", "Trocando em Miudos", "C", 0, 234,
     "Tom de Dó maior (home; modula Dó→Dó menor→Sol→Dó); cc_key C confirma a tônica home"),
    ("Chico Buarque", "Valsinha", "Am", 0, 250,
     "Tom de Lá menor; cc_key Cm = a MESMA tônica menor transposta (não a relativa) → "
     "offset 0 pelo papel, não Am−Cm"),
    ("Caetano Veloso", "Coracao Vagabundo", "Cm", 9, 263,
     "Tom de Dó menor; cc_key Eb = a relativa MAIOR → o CC anotou a relativa; centro real "
     "3 semitons abaixo (offset 9 = −3), invariante a transposição"),
]


def chediak_tonal_offset(song: str) -> Optional[Tuple[int, int]]:
    """`(structural_offset, página)` do tom citado de Chediak (Tier C) para a música,
    ou None se não houver fato. Chaveado pelo nome da música (como em `key_baseline`)."""
    for _artist, s, _tom, offset, page, _just in TIER_C_TONAL:
        if s == song:
            return offset, page
    return None


def chediak_center_pc(center_note: str) -> Optional[int]:
    try:
        return Note.parse(center_note).pitch_class
    except Exception:
        return None


def structural_offset(center_note: str, cc_key_pc: int) -> Optional[int]:
    """Offset do centro estrutural relativo ao tom do Cifra Club (invariante a
    transposição). Derivado do fato, não chutado."""
    pc = chediak_center_pc(center_note)
    return None if pc is None else (pc - cc_key_pc) % 12


# --- TIER B: verificação mecânica ao vivo (o crivo do trítono p/ proveniência) -

_CADENCE_WINDOW = 4  # acordes finais inspecionados (posição estrutural)


def verify_tonal_center(
    symbols: Sequence[str], cc_key_pc: int
) -> Tuple[bool, str]:
    """True se um V7/SubV7 FUNCIONAL (trítono: Category.DOMINANT) resolve no cc_key
    em posição estrutural/final — então o cc_key é a tônica por Chediak (p.84/87).

    Usa o trítono real (não qualquer acorde em V) e o baixo como alvo (lição da Sina).
    É o critério de PROVENIÊNCIA (Tier B), não o gate de detecção (change 2)."""
    roots: List[Optional[int]] = []
    basses: List[Optional[int]] = []
    is_dom: List[bool] = []
    for s in symbols:
        try:
            p = parse(s)
            roots.append(p.root.pitch_class)
            basses.append((p.bass or p.root).pitch_class)
            is_dom.append(_category(p) == "dominant")
        except Exception:
            roots.append(None)
            basses.append(None)
            is_dom.append(False)

    dom = (cc_key_pc + 7) % 12
    subv = (cc_key_pc + 1) % 12
    n = len(roots)
    # janela estrutural: o fim da progressão (encerramento crava a tonalidade)
    for i in range(max(0, n - _CADENCE_WINDOW), n - 1):
        if is_dom[i] and roots[i] in (dom, subv) and basses[i + 1] == cc_key_pc:
            kind = "V7" if roots[i] == dom else "SubV7"
            return True, f"{kind} funcional→I em posição final (acorde {i})"
    return False, "sem V7/SubV7 funcional resolvendo no cc_key na cadência final"
