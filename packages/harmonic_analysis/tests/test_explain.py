"""Camada 3 — explicação por porta `Explainer` + provedor de LLM plugável."""

import pytest

from harmonic_analysis.explain import (
    DEFAULT_MODEL,
    ExplainConfig,
    LLMConfig,
    OllamaProvider,
    OpenRouterProvider,
    TemplateExplainer,
    build_explainer,
    build_llm_provider,
)

SUBV_ANALYSIS = {
    "key": "C",
    "mode": "major",
    "cadences": {"Autêntica": {"G7 → C"}},
    "harmonic_analysis": [
        {"chord": "Db7", "function_code": "SubV"},
        {"chord": "C", "function_code": "T"},
    ],
}


def test_template_is_deterministic_and_offline():
    exp = TemplateExplainer()
    a = exp.explain(SUBV_ANALYSIS)
    b = exp.explain(SUBV_ANALYSIS)
    assert a == b  # mesma entrada → mesma saída
    assert a  # produz texto sem rede/chave


def test_template_explains_subv_referencing_tonic():
    text = TemplateExplainer().explain(SUBV_ANALYSIS)
    assert "Db7" in text
    assert "C" in text  # a tônica em que resolve
    assert "trítono" in text.lower() or "subv" in text.lower()


def test_template_states_key_and_authentic_cadence():
    text = TemplateExplainer().explain(SUBV_ANALYSIS)
    assert "C maior" in text
    assert "autêntica" in text.lower()


def test_no_engine_configured_uses_template():
    exp = build_explainer(ExplainConfig())  # engine padrão = template
    assert isinstance(exp, TemplateExplainer)


def test_llm_default_provider_and_model_are_free():
    provider = build_llm_provider(LLMConfig())  # sem provider/modelo explícito
    assert isinstance(provider, OpenRouterProvider)
    assert provider.model == "openrouter/free"
    assert DEFAULT_MODEL["openrouter"] == "openrouter/free"


def test_provider_and_model_switchable_by_config():
    provider = build_llm_provider(LLMConfig(provider="ollama", model="llama3.1"))
    assert isinstance(provider, OllamaProvider)
    assert provider.model == "llama3.1"


def test_unknown_provider_degrades_to_template():
    exp = build_explainer(
        ExplainConfig(engine="llm", llm=LLMConfig(provider="does-not-exist"))
    )
    assert isinstance(exp, TemplateExplainer)


def test_missing_credentials_degrades_to_template(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    exp = build_explainer(
        ExplainConfig(engine="llm", llm=LLMConfig(provider="openrouter"))
    )
    # Sem dependência (extra) ou sem chave → cai no template, nunca quebra.
    assert isinstance(exp, TemplateExplainer)


def test_llm_explainer_uses_injected_provider():
    # Provedor falso: o LLMExplainer delega sem tocar em rede.
    from harmonic_analysis.explain import LLMExplainer

    class FakeProvider:
        model = "fake"

        def preflight(self):
            return None

        def complete(self, system, user):
            assert "análise" in user.lower() or "harmôn" in user.lower()
            return "explicação via LLM"

    exp = LLMExplainer(FakeProvider())
    assert exp.explain(SUBV_ANALYSIS) == "explicação via LLM"


@pytest.mark.parametrize("provider", ["openrouter", "ollama", "anthropic"])
def test_every_provider_has_a_default_model(provider):
    assert provider in DEFAULT_MODEL and DEFAULT_MODEL[provider]
