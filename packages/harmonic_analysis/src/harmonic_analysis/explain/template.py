"""Explainer padrão: determinístico, offline, sem LLM (Camada 3 — D4)."""

from __future__ import annotations

from harmonic_analysis.explain.prompt import render_summary, summarize_facts


class TemplateExplainer:
    """Gera prosa pedagógica a partir da análise — sem rede, sem chave.

    É o padrão geral: a análise jamais depende de um LLM. Mesma entrada → mesma
    saída (determinístico).
    """

    def explain(self, analysis: dict) -> str:
        facts = summarize_facts(analysis)
        return " ".join(render_summary(facts))
