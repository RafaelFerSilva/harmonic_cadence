"""Camada de explicação (Camada 3 — D4).

Duas portas em composição:
- `Explainer`: transforma uma análise harmônica em prosa pedagógica;
- `LLMProvider`: abstrai o **provedor de IA e o modelo** (registro extensível).

O padrão geral é o `TemplateExplainer`: determinístico, offline, sem chave. O
`LLMExplainer` é opt-in e usa um `LLMProvider` plugável (OpenRouter por padrão,
com o modelo gratuito `openrouter/free`). Qualquer falha degrada para o template.
"""

from harmonic_analysis.explain.base import (
    ExplainConfig,
    Explainer,
    build_explainer,
)
from harmonic_analysis.explain.llm import (
    DEFAULT_MODEL,
    PROVIDERS,
    AnthropicProvider,
    LLMConfig,
    LLMExplainer,
    LLMProvider,
    MissingCredentials,
    MissingDependency,
    OllamaProvider,
    OpenRouterProvider,
    build_llm_provider,
)
from harmonic_analysis.explain.template import TemplateExplainer

__all__ = [
    "Explainer",
    "ExplainConfig",
    "build_explainer",
    "TemplateExplainer",
    "LLMExplainer",
    "LLMProvider",
    "LLMConfig",
    "build_llm_provider",
    "PROVIDERS",
    "DEFAULT_MODEL",
    "OpenRouterProvider",
    "OllamaProvider",
    "AnthropicProvider",
    "MissingCredentials",
    "MissingDependency",
]
