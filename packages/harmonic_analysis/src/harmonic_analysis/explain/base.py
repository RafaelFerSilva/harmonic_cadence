"""Porta `Explainer` e raiz de composição (Camada 3 — D4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from harmonic_analysis.explain.llm import (
    LLMConfig,
    LLMExplainer,
    MissingCredentials,
    MissingDependency,
    build_llm_provider,
)
from harmonic_analysis.explain.template import TemplateExplainer


@runtime_checkable
class Explainer(Protocol):
    """Porta de explicação: análise (dict) → prosa (str)."""

    def explain(self, analysis: dict) -> str: ...


@dataclass
class ExplainConfig:
    """Seleção do motor de explicação.

    `engine="template"` (padrão) é offline/determinístico. `engine="llm"` ativa o
    `LLMExplainer` sobre o provedor configurado em `llm`.
    """

    engine: str = "template"  # "template" | "llm"
    llm: LLMConfig = field(default_factory=LLMConfig)


def build_explainer(cfg: ExplainConfig) -> Explainer:
    """Monta o explainer ativo. Qualquer falha do LLM degrada para o template."""
    if getattr(cfg, "engine", "template") == "llm":
        try:
            provider = build_llm_provider(cfg.llm)
            provider.preflight()  # falha cedo (dep/credencial) → fallback
            return LLMExplainer(provider)
        except (ImportError, KeyError, MissingDependency, MissingCredentials):
            return TemplateExplainer()
    return TemplateExplainer()
