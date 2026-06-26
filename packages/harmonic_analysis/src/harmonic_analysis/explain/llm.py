"""Camada de provedores de LLM plugável (Camada 3 — D4 / Appendix B).

`LLMProvider` é a porta (provedor + modelo escolhíveis). Os adaptadores ficam num
registro `PROVIDERS`; o modelo-padrão por provedor em `DEFAULT_MODEL`. Provedores
OpenAI-compatíveis (OpenRouter, Ollama) compartilham um cliente HTTP — só mudam
`base_url`/chave. A SDK só é importada na hora de chamar (`complete`), e a
disponibilidade é checada no `preflight` para permitir fallback gracioso.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from harmonic_analysis.explain.prompt import build_prompt


class MissingDependency(ImportError):
    """Extra/SDK do provedor ausente (ex.: `[explain-llm]` não instalado)."""


class MissingCredentials(RuntimeError):
    """Credencial do provedor ausente (variável de ambiente não definida)."""


@runtime_checkable
class LLMProvider(Protocol):
    """Porta de provedor de IA: produz uma completude a partir de system+user."""

    model: str

    def preflight(self) -> None:
        """Valida dependência/credenciais; levanta antes de qualquer chamada."""
        ...

    def complete(self, system: str, user: str) -> str: ...


class _OpenAICompatProvider:
    """Base para provedores OpenAI-compatíveis (OpenRouter, Ollama)."""

    base_url = ""
    env_key = ""  # vazio = não requer credencial
    requires = "openai"

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model
        self._api_key = api_key
        self._base_url = base_url or self.base_url

    def _resolve_key(self) -> Optional[str]:
        if self._api_key:
            return self._api_key
        if self.env_key:
            return os.environ.get(self.env_key)
        return None

    def preflight(self) -> None:
        if importlib.util.find_spec(self.requires) is None:
            raise MissingDependency(
                f"O provedor requer o pacote '{self.requires}' "
                "(instale o extra [explain-llm])."
            )
        if self.env_key and not self._resolve_key():
            raise MissingCredentials(
                f"Defina {self.env_key} para usar este provedor."
            )

    def complete(self, system: str, user: str) -> str:
        self.preflight()
        from openai import OpenAI  # import tardio — só quando realmente chamado

        client = OpenAI(
            base_url=self._base_url,
            api_key=self._resolve_key() or "not-needed",
        )
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""


class OpenRouterProvider(_OpenAICompatProvider):
    """PADRÃO de LLM — OpenAI-compatível, modelo gratuito `openrouter/free`."""

    base_url = "https://openrouter.ai/api/v1"
    env_key = "OPENROUTER_API_KEY"


class OllamaProvider(_OpenAICompatProvider):
    """Local/offline (sem chave) — servidor Ollama OpenAI-compatível."""

    base_url = "http://localhost:11434/v1"
    env_key = ""  # sem credencial


class AnthropicProvider:
    """Adaptador opcional para a SDK Anthropic (Claude)."""

    requires = "anthropic"
    env_key = "ANTHROPIC_API_KEY"

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model
        self._api_key = api_key
        self._base_url = base_url

    def _resolve_key(self) -> Optional[str]:
        return self._api_key or os.environ.get(self.env_key)

    def preflight(self) -> None:
        if importlib.util.find_spec(self.requires) is None:
            raise MissingDependency(
                "O provedor Anthropic requer o pacote 'anthropic'."
            )
        if not self._resolve_key():
            raise MissingCredentials(f"Defina {self.env_key} para usar o Claude.")

    def complete(self, system: str, user: str) -> str:
        self.preflight()
        import anthropic  # import tardio

        client = anthropic.Anthropic(api_key=self._resolve_key())
        msg = client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(
            block.text for block in msg.content if getattr(block, "type", "") == "text"
        )


# Registro de provedores — adicionar um adaptador novo não toca no LLMExplainer.
PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}

# Modelo-padrão por provedor (gratuito quando possível).
DEFAULT_MODEL = {
    "openrouter": "openrouter/free",
    "ollama": "llama3.1",
    "anthropic": "claude-haiku-4-5-20251001",
}


@dataclass
class LLMConfig:
    """Configuração do provedor de IA (provedor + modelo plugáveis)."""

    provider: str = "openrouter"  # chave do registro PROVIDERS
    model: Optional[str] = None  # None → DEFAULT_MODEL[provider]
    api_key: Optional[str] = None  # senão, variável de ambiente do provedor
    base_url: Optional[str] = None


def build_llm_provider(cfg: LLMConfig) -> LLMProvider:
    """Monta o provedor a partir da config (KeyError se o provedor é desconhecido)."""
    cls = PROVIDERS[cfg.provider]  # KeyError → fallback no build_explainer
    model = cfg.model or DEFAULT_MODEL[cfg.provider]
    return cls(model=model, api_key=cfg.api_key, base_url=cfg.base_url)


class LLMExplainer:
    """Explainer que delega a um `LLMProvider` injetado.

    Explica **a partir da análise determinística** (fundamentado, auditável);
    não re-analisa a música.
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def explain(self, analysis: dict) -> str:
        system, user = build_prompt(analysis)
        return self.provider.complete(system, user)
