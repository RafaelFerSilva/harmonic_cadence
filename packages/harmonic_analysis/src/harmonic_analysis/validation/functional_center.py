"""Centro tonal pelo critério FUNCIONAL do Chediak — achado da música, sem anotação.

O Cifra Club é só fonte de cifra; o `cc_key` não é ouro de nada. Chediak é a base: a
tônica é repouso, e um dominante FUNCIONAL (trítono real, `Category.DOMINANT`) — V7 (5ªJ
acima) ou SubV7 (½t acima) — resolvendo pelo baixo num acorde de repouso ESTABELECE a
tônica (Vol. I pp.84/87). `chediak_functional_center` ENCONTRA essa tônica direto dos
acordes, sem `cc_key`, e é invariante a transposição.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

from cifra_core.theory.chord_parse import parse


def _category(p) -> str:
    c = p.category
    return (c() if callable(c) else c).value


def chediak_functional_center(
    symbols: Sequence[str],
) -> Optional[Tuple[int, str]]:
    """ENCONTRA a tônica pelo critério funcional do Chediak (pp.84/87), só da música.

    Ancora o candidato a tônica nos REPOUSOS estruturais — o último acorde (a cadência
    final é o sinal mais forte da tônica) e, em seguida, o primeiro — e o CONFIRMA pelo
    critério funcional: um dominante real (trítono, `Category.DOMINANT`) — V7 (5ªJ acima)
    ou SubV7 (½t acima) — resolvendo pelo BAIXO naquele candidato.

    Restringir o alvo a um EXTREMO da peça evita o falso-positivo do dominante SECUNDÁRIO
    (V7/IV→IV não faz da IV a tônica, pois a IV não é extremo). Como o centro aqui é
    CORROBORAÇÃO (não ouro), imperfeições residuais viram item de worklist, não gold falso.

    Retorna `(pitch_class, modo)` — modo pela QUALIDADE do acorde de repouso (menor →
    "minor", senão "major") — ou None se nenhuma resolução funcional ancorar um extremo.
    NENHUMA anotação de fonte entra; invariante a transposição."""
    roots: List[Optional[int]] = []
    basses: List[Optional[int]] = []
    is_dom: List[bool] = []
    qual: List[str] = []
    for s in symbols:
        try:
            p = parse(s)
            roots.append(p.root.pitch_class)
            basses.append((p.bass or p.root).pitch_class)
            is_dom.append(_category(p) == "dominant")
            qual.append(_category(p))
        except Exception:
            roots.append(None)
            basses.append(None)
            is_dom.append(False)
            qual.append("")

    n = len(roots)
    valid_bass = [b for b in basses if b is not None]
    if not valid_bass:
        return None
    # Repousos estruturais: último (cadência final, sinal mais forte) e depois o primeiro.
    candidates: List[int] = []
    for cand in (valid_bass[-1], valid_bass[0]):
        if cand not in candidates:
            candidates.append(cand)

    for cand in candidates:
        dom = (cand + 7) % 12
        subv = (cand + 1) % 12
        for i in range(n - 1):
            # O alvo da resolução só ESTABELECE tônica se for um REPOUSO (Chediak pp.84-85):
            #   • não-dominante (sem trítono real) — senão é elo de cadeia V/V→V, não chegada;
            #   • raiz == baixo — a tônica repousa na própria raiz; rejeita inversão (Fm/C).
            if (
                is_dom[i]
                and roots[i] in (dom, subv)
                and basses[i + 1] == cand
                and not is_dom[i + 1]
                and roots[i + 1] == basses[i + 1]
            ):
                mode = "minor" if qual[i + 1] == "minor" else "major"
                return cand, mode
    return None
