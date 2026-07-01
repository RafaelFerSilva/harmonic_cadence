"""Observabilidade: seções opcionais degradam visíveis, não em silêncio."""

import logging

from harmonic_analysis.domain import voice_leading
from harmonic_analysis.services.analysis_service import AnalysisService

DATA = {"name": "x", "artist": "y", "cifra": ["C  F  G7  C", "Am  Dm7  G7  Cmaj7"]}


def test_clean_run_has_empty_diagnostics():
    res = AnalysisService(None).analyze_song_data_structured(DATA)
    assert res["success"]
    assert res["diagnostics"] == []


def test_unidentified_notation_is_reported_in_diagnostics():
    # 'D9/S' (baixo inválido) é notação não identificada: reportada, não silenciosa nem chutada.
    data = {"name": "x", "artist": "y", "cifra": ["D9/S / E/D / D9/S / D7(9) / D9/S"]}
    res = AnalysisService(None).analyze_song_data_structured(data)
    assert res["success"]  # a música é analisada com os acordes válidos
    errors = [
        d["error"] for d in res["diagnostics"] if d["section"] == "chord_extraction"
    ]
    assert any("D9/S" in e for e in errors)  # a notação é nomeada
    # o prefixo 'D9' NÃO foi chutado como acorde
    assert all(c["chord"] != "D9" for c in res["harmonic_analysis"])


def test_section_error_is_recorded_logged_not_swallowed(monkeypatch, caplog):
    def boom(*_a, **_k):
        raise ValueError("falha proposital")

    monkeypatch.setattr(voice_leading, "analyze", boom)
    with caplog.at_level(logging.WARNING):
        res = AnalysisService(None).analyze_song_data_structured(DATA)

    assert res["success"]                 # resto da análise segue
    assert res["voice_leading"] == {}     # default da seção
    sections = {d["section"] for d in res["diagnostics"]}
    assert "voice_leading" in sections    # registrado em diagnostics
    assert "falha proposital" in next(
        d["error"] for d in res["diagnostics"] if d["section"] == "voice_leading"
    )
    assert any("voice_leading" in r.getMessage() for r in caplog.records)  # logado
