"""`analyze --engine llm` regenera a explicação do relatório via LLM (opt-in)."""

import argparse

import harmonic_analysis.explain as explain_mod
from harmonic_analysis.cli.main import HarmonicCLI


def _args(**kw):
    ns = argparse.Namespace(
        engine="template", llm_provider="openrouter", llm_model=None
    )
    for k, v in kw.items():
        setattr(ns, k, v)
    return ns


def test_template_engine_leaves_explanation_untouched():
    result = {"explanation": "TEMPLATE", "key": "C"}
    HarmonicCLI()._apply_explanation_engine(result, _args(engine="template"))
    assert result["explanation"] == "TEMPLATE"


def test_llm_engine_overrides_explanation(monkeypatch):
    class _Fake:
        def explain(self, analysis):
            return "LLM-TEXT"

    monkeypatch.setattr(explain_mod, "build_explainer", lambda cfg: _Fake())
    result = {"explanation": "TEMPLATE", "key": "C"}
    HarmonicCLI()._apply_explanation_engine(result, _args(engine="llm"))
    assert result["explanation"] == "LLM-TEXT"


def test_llm_engine_without_key_keeps_template(monkeypatch, tmp_path):
    # dir limpo (sem .env) + sem a variável → garante ausência de credencial
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    result = {"explanation": "TEMPLATE", "key": "C"}
    HarmonicCLI()._apply_explanation_engine(result, _args(engine="llm"))
    # sem chave/dep/provedor → fallback gracioso mantém o template
    assert result["explanation"] == "TEMPLATE"


def test_llm_engine_network_failure_keeps_template(monkeypatch):
    class _Boom:
        def explain(self, analysis):
            raise RuntimeError("network down")

    monkeypatch.setattr(explain_mod, "build_explainer", lambda cfg: _Boom())
    result = {"explanation": "TEMPLATE", "key": "C"}
    HarmonicCLI()._apply_explanation_engine(result, _args(engine="llm"))
    assert result["explanation"] == "TEMPLATE"  # falha não quebra nem apaga


def test_analyze_parser_accepts_llm_flags():
    ns = HarmonicCLI().parser.parse_args(
        ["analyze", "Djavan", "Sina", "--engine", "llm", "--format", "html"]
    )
    assert ns.engine == "llm"
    assert ns.llm_provider == "openrouter"
    # default permanece template quando a flag não é dada
    ns2 = HarmonicCLI().parser.parse_args(["analyze", "Djavan", "Sina"])
    assert ns2.engine == "template"
