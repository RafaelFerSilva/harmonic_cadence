"""Nota do curador — centro modal (change `modal-center-arbitration`, parte B).

O centro modal de Chediak é um FATO curado anotado na exibição (Caminho 2), nunca
detectado das cifras. O render lê só o dataset curado + a identidade da análise:
match → blockquote (MD) / callout (HTML) com a citação; miss → relatório
byte-idêntico ao de hoje. Não toca detecção nem muta o JSON.
"""

import json
import os
import tempfile

from harmonic_analysis.corpus.modal_centers import Citation
from harmonic_analysis.presentation.labels import format_citation, interval_pt
from harmonic_analysis.presentation.reports.html import HTMLReportGenerator
from harmonic_analysis.presentation.reports.json import JSONReportGenerator
from harmonic_analysis.presentation.reports.markdown import MarkdownReportGenerator


# --- 5.0 unidade do formatador de citação ------------------------------------

def test_format_citation_uses_roman_volume():
    c = Citation(source="Almir Chediak, Harmonia & Improvisação", volume=1, page=125)
    assert format_citation(c) == (
        "Almir Chediak, Harmonia & Improvisação, Vol. I, p. 125"
    )


def test_interval_pt_names_the_fifth():
    assert interval_pt(7) == "5ª justa"
    assert interval_pt(3) == "3ª menor"


# --- fixtures de análise ------------------------------------------------------

def _analysis(**over):
    base = {
        "artist": "Edu Lobo",
        "name": "Arrastao",
        "key": "D",
        "mode": "major",
        "unique_chords": ["D", "Am7", "G"],
        "harmonic_analysis": [],
        "cadences": {},
        "chord_qualities": {"major": 2, "minor": 1},
        "function_stats": {},
        "analysis_progression": [],
        "cifra_lines": [],
    }
    base.update(over)
    return base


# --- 5.1 markdown -------------------------------------------------------------

def test_markdown_renders_curator_note_for_curated_song():
    header = MarkdownReportGenerator()._generate_header(_analysis(), "http://yt")
    assert "Nota do curador" in header
    assert "A dórico" in header  # centro de Chediak
    assert "5ª justa" in header  # finalis transposição-segura (offset 7)
    assert "Vol. I, p. 125" in header  # a citação como atribuição


def test_markdown_no_curator_note_for_unknown_song():
    header = MarkdownReportGenerator()._generate_header(
        _analysis(artist="Tom Jobim", name="Garota de Ipanema"), "http://yt"
    )
    assert "Nota do curador" not in header


def test_markdown_curator_note_does_not_mutate_analysis():
    a = _analysis()
    MarkdownReportGenerator()._generate_header(a, "http://yt")
    assert a["key"] == "D" and a["mode"] == "major"
    assert "modal_center" not in a


# --- 5.2 html -----------------------------------------------------------------

def test_html_renders_curator_callout_for_curated_song():
    html = HTMLReportGenerator()._generate_html_document(
        _analysis(), "http://yt", 3, 2, 1, 66.0, 33.0
    )
    assert "Nota do curador" in html
    assert "<cite" in html
    assert "blockquote-footer" in html
    assert "Vol. I, p. 125" in html
    # `&` da fonte é escapado no HTML.
    assert "Harmonia &amp; Improvisa" in html


def test_html_no_callout_for_unknown_song():
    html = HTMLReportGenerator()._generate_html_document(
        _analysis(artist="Tom Jobim", name="Garota de Ipanema"),
        "http://yt", 3, 2, 1, 66.0, 33.0,
    )
    assert "Nota do curador" not in html


# --- 5.4 json carrega a citação ESTRUTURADA ----------------------------------

def test_json_carries_structured_citation():
    a = _analysis()
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            path = JSONReportGenerator().generate(a, filename="out.json")
            report = json.load(open(path, encoding="utf-8"))
        finally:
            os.chdir(cwd)
    mc = report["key_analysis"]["modal_center"]
    assert mc["center"] == "A"
    assert mc["mode"] == "dorian"
    assert mc["finalis_from_tonal"] == 7
    # citação ESTRUTURADA, não a string montada
    assert mc["citation"] == {
        "source": "Almir Chediak, Harmonia & Improvisação",
        "volume": 1,
        "page": 125,
    }
    assert a.get("modal_center") is None  # não mutou o dict de análise


def test_json_omits_modal_center_for_unknown_song():
    a = _analysis(artist="Tom Jobim", name="Garota de Ipanema")
    with tempfile.TemporaryDirectory() as tmp:
        cwd = os.getcwd()
        os.chdir(tmp)
        try:
            path = JSONReportGenerator().generate(a, filename="out.json")
            report = json.load(open(path, encoding="utf-8"))
        finally:
            os.chdir(cwd)
    assert "modal_center" not in report["key_analysis"]
