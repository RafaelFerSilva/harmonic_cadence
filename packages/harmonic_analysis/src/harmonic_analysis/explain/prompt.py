"""Resumo da análise e construção de prompt para o explainer por LLM.

O resumo determinístico é a **fonte única de fatos**: o `TemplateExplainer` o usa
para gerar prosa offline, e o `LLMExplainer` o injeta no prompt para que o modelo
explique *a partir da análise* (sem re-analisar a música).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from harmonic_analysis.presentation.labels import church_mode_pt, mode_pt


def _unique(items: List[str]) -> List[str]:
    """Remove duplicatas preservando a ordem de primeira aparição."""
    seen: set = set()
    out: List[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def summarize_facts(analysis: dict) -> Dict[str, object]:
    """Extrai os fatos harmônicos relevantes da análise determinística."""
    key = analysis.get("key")
    mode = analysis.get("mode")
    ha = analysis.get("harmonic_analysis", []) or []

    sub_v = _unique([e["chord"] for e in ha if e.get("function_code") == "SubV"])
    secondary = _unique([e["chord"] for e in ha if e.get("function_code") == "Dsec"])
    borrowed = _unique([e["chord"] for e in ha if e.get("function_code") == "Emp"])

    cadences = analysis.get("cadences") or {}
    authentic = sorted(
        list(cadences.get("Autêntica", []) or [])
        + list(cadences.get("Perfeita", []) or [])
    )
    plagal = sorted(cadences.get("Plagal", []) or [])

    modal = analysis.get("modal_analysis")
    coloring = analysis.get("modal_coloring")

    return {
        "key": key,
        "mode": mode,
        "chords": [e.get("chord") for e in ha if e.get("chord")],
        "sub_v": sub_v,
        "secondary": secondary,
        "borrowed": borrowed,
        "authentic": authentic,
        "plagal": plagal,
        "modal": modal,
        "coloring": coloring,
    }


def _join_capped(items: List[str], limit: int = 4) -> str:
    """Junta uma lista limitando o tamanho, com 'entre outros' quando excede."""
    if len(items) <= limit:
        return ", ".join(items)
    return ", ".join(items[:limit]) + ", entre outros"


def render_summary(facts: Dict[str, object]) -> List[str]:
    """Transforma os fatos em linhas de prosa pedagógica (determinístico)."""
    lines: List[str] = []
    key, mode = facts.get("key"), facts.get("mode")
    if key:
        lines.append(f"A música está em {key} {mode_pt(mode)}.")

    modal = facts.get("modal")
    if modal:
        lines.append(
            f"O centro tonal é modal: {modal['tonic']} {church_mode_pt(modal['mode'])}."
        )

    coloring = facts.get("coloring")
    if coloring:
        ev = "; ".join(coloring.get("evidence") or [])
        lines.append(
            f"A peça é tonal, com coloração {church_mode_pt(coloring['flavor'])}"
            f"{f' ({ev})' if ev else ''} — uma cor modal sobre a leitura tonal."
        )

    if facts.get("authentic"):
        exemplos = ", ".join(facts["authentic"][:3])  # type: ignore[index]
        lines.append(
            f"Há cadência autêntica (dominante → tônica): {exemplos}."
        )
    if facts.get("plagal"):
        exemplos = ", ".join(facts["plagal"][:3])  # type: ignore[index]
        lines.append(f"Há cadência plagal (subdominante → tônica): {exemplos}.")

    if facts.get("sub_v"):
        chords = _join_capped(facts["sub_v"])  # type: ignore[arg-type]
        lines.append(
            f"O acorde {chords} é um substituto de trítono (SubV), um dominante "
            f"que resolve por meio-tom na tônica {key}."
        )
    if facts.get("secondary"):
        chords = _join_capped(facts["secondary"])  # type: ignore[arg-type]
        lines.append(
            f"Há dominante(s) secundário(s) ({chords}), tonicalizando graus "
            "internos antes de retornar à tônica."
        )
    if facts.get("borrowed"):
        chords = _join_capped(facts["borrowed"])  # type: ignore[arg-type]
        lines.append(
            f"Há empréstimo modal ({chords}), acordes vindos do modo paralelo."
        )

    if not lines:
        lines.append("Não há eventos harmônicos destacáveis nesta análise.")
    return lines


def build_prompt(analysis: dict) -> Tuple[str, str]:
    """Monta (system, user) para o LLM a partir do resumo determinístico."""
    facts = summarize_facts(analysis)
    summary = "\n".join(f"- {line}" for line in render_summary(facts))
    system = (
        "Você é um professor de harmonia da música popular brasileira. Explique a "
        "análise harmônica de forma clara, pedagógica e fiel aos fatos fornecidos. "
        "Não invente acordes ou funções que não estejam no resumo."
    )
    user = (
        "Com base nesta análise harmônica determinística, escreva uma explicação "
        f"em português, curta e didática:\n\n{summary}"
    )
    return system, user
