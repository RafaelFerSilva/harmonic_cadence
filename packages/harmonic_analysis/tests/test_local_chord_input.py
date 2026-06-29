"""Entrada de acordes local (change `local-chord-input`).

Analisa acordes de um `.txt`/string pelo MESMO motor, sem Cifra Club e sem rede. A
tonalidade vem do `detect_key` (sem "Tom:" da fonte). Núcleo intocado.
"""

import os

import pytest

from cifra_core import cifra_from_text
from harmonic_analysis.cli.main import HarmonicCLI
from harmonic_analysis.services.analysis_service import AnalysisService


# --- 3.2 paridade de motor: fonte local = fonte raspada -----------------------

def test_local_source_detects_key_from_chords():
    # Sem provider de rede: a análise roda por analyze_song_data_structured.
    service = AnalysisService()
    cifra = cifra_from_text("C  Am  Dm  G7\nC  Am  Dm  G7  C", title="prog")
    result = service.analyze_song_data_structured(cifra.to_dict())
    assert "error" not in result
    assert result["key"] == "C"  # detectado dos acordes, não de um "Tom:"


def test_local_and_dict_source_are_identical():
    # Mesmos acordes via cifra_from_text e via dict cru → mesma leitura tonal.
    service = AnalysisService()
    chords_dict = {"artist": "", "name": "p", "cifra": ["C  Am  Dm  G7  C"]}
    via_text = service.analyze_song_data_structured(
        cifra_from_text("C  Am  Dm  G7  C", title="p").to_dict()
    )
    via_dict = service.analyze_song_data_structured(chords_dict)
    assert via_text["key"] == via_dict["key"]
    assert via_text["mode"] == via_dict["mode"]


def test_service_needs_no_provider_for_local():
    # O caminho local não constrói provider de rede.
    assert AnalysisService().provider is None


# --- 3.3 CLI analyze-file -----------------------------------------------------

def test_cli_analyze_file_generates_report(tmp_path, monkeypatch):
    f = tmp_path / "prog.txt"
    f.write_text("C  Am  Dm  G7\nC  Am  Dm  G7  C", encoding="utf-8")
    monkeypatch.chdir(tmp_path)  # relatórios são escritos no cwd
    HarmonicCLI().run(["analyze-file", str(f), "--format", "json"])
    assert os.path.isdir(tmp_path / "report_json")
    assert any((tmp_path / "report_json").iterdir())


def test_cli_analyze_file_missing_exits_nonzero(tmp_path):
    with pytest.raises(SystemExit) as exc:
        HarmonicCLI().run(["analyze-file", str(tmp_path / "nope.txt")])
    assert exc.value.code == 1


def test_cli_analyze_file_no_chords_exits_nonzero(tmp_path):
    f = tmp_path / "lyrics.txt"
    f.write_text("apenas letra\nsem acordes aqui", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        HarmonicCLI().run(["analyze-file", str(f)])
    assert exc.value.code == 1
