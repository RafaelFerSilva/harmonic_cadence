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


def _category(p) -> str:
    c = p.category
    return (c() if callable(c) else c).value


# --- TIER A: fatos de centro do Chediak (Parte 2, pp.121-127) -----------------
# (artista, música, centro_Chediak, modo, página, nota). RESERVADO para a change 2
# (arbitragem modal de centro). NÃO usado na métrica TONAL da change 1: a derivação do
# offset por subtração absoluta `(centro_Chediak − cc_key)` só vale quando Chediak e o
# Cifra Club estão na MESMA transposição — falso em "Pra Não Dizer" (Chediak Mi, CC Fá)
# e suspeito em "Procissão". A change 2 trata a transposição modal direito (offset pelo
# grau do final na coleção, não por altura absoluta). Aqui ficam só como fatos citados.
TIER_A_CHEDIAK = [
    ("Edu Lobo", "Arrastao", "A", "dorian", 125,
     "Lá dórico; o final dórico diverge do eixo tonal que o CC/K-S leem"),
    ("Edu Lobo", "Upa Neguinho", "D", "mixolydian", 126,
     "Ré mixolídio (centro = Ré; só o modo diverge do tonal)"),
    ("Gilberto Gil", "Procissao", "C", "mixolydian", 126,
     "Dó mixolídio (centro = Dó)"),
    ("Geraldo Vandre", "Pra Nao Dizer Que Nao Falei das Flores", "E", "aeolian", 127,
     "Mi eólio = menor natural; centro = Mi"),
]


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
