"""Relatórios exibem as seções das Camadas 2 e 3, com omissão graciosa."""

import json

from harmonic_analysis.presentation.reports.factory import ReportFactory
from harmonic_analysis.services.analysis_service import AnalysisService


def _analyze(cifra_lines):
    return AnalysisService(None).analyze_song_data_structured(
        {"name": "Teste", "artist": "Artista", "cifra": cifra_lines}
    )


# Peça tonal rica: inversões, ii-V, dominante — modal_analysis é None.
TONAL = ["C  C/E  F  G7/B", "Am  Dm7  G7  Cmaj7"]
# Peça modal: G mixolídio (bVII = F).
MODAL = ["G F C G", "G F C G"]
# Peça tonal (Sol maior, ancorada pelo D7=V) com coloração mixolídia: bVII (F) → I (G).
MIXO_COLORING = ["G D7 G F", "G C G F", "G D7 G F"]


def test_json_includes_depth_and_intelligence(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = ReportFactory.create("json").generate(_analyze(TONAL))
    report = json.loads(open(path, encoding="utf-8").read())

    assert "depth" in report
    assert report["depth"]["roman_numerals"][:2] == ["I", "I6"]
    assert "voice_leading" in report["depth"]
    assert "chord_scales" in report["depth"]

    assert "intelligence" in report
    assert "functional_parse" in report["intelligence"]
    assert any(
        s["technique"] == "tritone_substitution"
        for s in report["intelligence"]["reharmonizations"]
    )
    assert isinstance(report["intelligence"]["explanation"], str)


def test_json_omits_absent_modal_section(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = ReportFactory.create("json").generate(_analyze(TONAL))
    report = json.loads(open(path, encoding="utf-8").read())
    # peça tonal: modal_analysis é None → chave omitida (não emitida como null)
    assert "modal_analysis" not in report.get("depth", {})


def test_json_omits_modal_even_for_modal_progression(monkeypatch, tmp_path):
    # Detecção automática de modo removida (fix-or-remove-church-mode): mesmo uma
    # progressão modal limpa não gera seção modal → omitida do relatório.
    monkeypatch.chdir(tmp_path)
    path = ReportFactory.create("json").generate(_analyze(MODAL))
    report = json.loads(open(path, encoding="utf-8").read())
    assert "modal_analysis" not in report.get("depth", {})


def test_markdown_renders_explanation_reharmonizations_and_romans(
    monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    path = ReportFactory.create("markdown").generate(_analyze(TONAL))
    text = open(path, encoding="utf-8").read()
    assert "## Explicação" in text
    assert "## Sugestões de reharmonização" in text
    assert "tritone_substitution" in text
    assert "## Cifragem romana" in text


def test_markdown_omits_empty_reharmonizations(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    r = _analyze(TONAL)
    r["reharmonizations"] = []  # força lista vazia
    path = ReportFactory.create("markdown").generate(r)
    text = open(path, encoding="utf-8").read()
    assert "## Sugestões de reharmonização" not in text


def test_markdown_renders_modal_coloring_when_present(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    r = _analyze(MIXO_COLORING)
    assert r["modal_coloring"] is not None  # tonal G maior + cor mixolídia
    assert r["key"] == "G" and r["mode"] == "major"  # cabeçalho segue tonal
    path = ReportFactory.create("markdown").generate(r)
    text = open(path, encoding="utf-8").read()
    assert "## Coloração modal" in text
    assert "mixolídio" in text


def test_markdown_omits_modal_coloring_when_absent(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    r = _analyze(TONAL)
    assert r["modal_coloring"] is None
    path = ReportFactory.create("markdown").generate(r)
    text = open(path, encoding="utf-8").read()
    assert "## Coloração modal" not in text


def test_html_includes_new_sections(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    path = ReportFactory.create("html").generate(_analyze(TONAL))
    html = open(path, encoding="utf-8").read()
    assert "Explicação" in html
    assert "Cifragem romana" in html
    assert "Sugestões de reharmonização" in html
    assert "Parsing funcional" in html


def test_reports_preserve_existing_sections(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    # Markdown: seções clássicas seguem presentes
    md = open(
        ReportFactory.create("markdown").generate(_analyze(TONAL)), encoding="utf-8"
    ).read()
    assert "## Estatísticas Gerais" in md
    assert "## Análise harmônica dos acordes" in md
    assert "## Cadências encontradas" in md

    # JSON: chaves clássicas intactas
    report = json.loads(
        open(
            ReportFactory.create("json").generate(_analyze(TONAL)), encoding="utf-8"
        ).read()
    )
    for key in ("metadata", "statistics", "harmonic_analysis", "cadences", "raw_data"):
        assert key in report
