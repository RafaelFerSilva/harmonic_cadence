"""Nomeação de modo grego no display (change `modal-mode-naming`, parte A).

Promoção de DISPLAY do `modal_coloring.flavor` a um nome de modo fundido ao centro
tonal ("D mixolídio"). Não toca detecção: o JSON canônico segue inalterado; sem
coloração o cabeçalho é byte-idêntico ao tonal puro. Eólio silencioso, dórico fora.
"""

from harmonic_analysis.explain.prompt import render_summary, summarize_facts
from harmonic_analysis.presentation.labels import modal_mode_name
from harmonic_analysis.presentation.reports.html import HTMLReportGenerator
from harmonic_analysis.presentation.reports.markdown import MarkdownReportGenerator


# --- 3.1 unidade da função de rótulo -----------------------------------------

def test_modal_mode_name_fuses_tonic_and_greek_mode():
    assert modal_mode_name("D", "mixolydian") == "D mixolídio"
    assert modal_mode_name("D", "phrygian") == "D frígio"


def test_modal_mode_name_spells_flats():
    # Mantém a grafia da tônica vinda do detect_key (Note soletrada).
    assert modal_mode_name("Bb", "mixolydian") == "Bb mixolídio"


def test_modal_mode_name_non_nameable_returns_plain_tonic():
    # Eólio e dórico NUNCA viram nome aqui (não são flavors do detect_coloring).
    assert modal_mode_name("D", "aeolian") == "D"
    assert modal_mode_name("D", "dorian") == "D"
    assert modal_mode_name("D", "") == "D"
    assert modal_mode_name("D", None) == "D"


# --- 3.2 render (markdown + html) --------------------------------------------

def _analysis(**over):
    base = {
        "artist": "Edu Lobo",
        "name": "Upa Neguinho",
        "key": "D",
        "mode": "major",
        "unique_chords": ["D", "Am7", "G"],
        "harmonic_analysis": [],
        "cadences": {},
        "chord_qualities": {"major": 2, "minor": 1},
        "function_stats": {},
        "analysis_progression": [],
    }
    base.update(over)
    return base


def test_markdown_header_names_mode_when_coloring_present():
    a = _analysis(modal_coloring={"flavor": "mixolydian", "evidence": ["v menor recorrente (2×)"], "where": [1]})
    header = MarkdownReportGenerator()._generate_header(a, "http://yt")
    assert "Centro modal:** D mixolídio" in header
    # A leitura tonal continua presente, ao lado (não substituída).
    assert "Tonalidade sugerida:** D (maior)" in header


def test_markdown_header_unchanged_without_coloring():
    a = _analysis(modal_coloring=None)
    header = MarkdownReportGenerator()._generate_header(a, "http://yt")
    assert "Centro modal" not in header
    assert "Tonalidade sugerida:** D (maior)" in header


def test_html_header_names_mode_when_coloring_present():
    a = _analysis(modal_coloring={"flavor": "phrygian", "evidence": ["bII→i (2×)"], "where": [3]}, key="D", mode="minor")
    html = HTMLReportGenerator()._generate_html_document(a, "http://yt", 3, 1, 1, 33.0, 33.0)
    assert "Centro modal:</strong> D frígio" in html


def test_html_header_unchanged_without_coloring():
    a = _analysis(modal_coloring=None)
    html = HTMLReportGenerator()._generate_html_document(a, "http://yt", 3, 2, 1, 66.0, 33.0)
    assert "Centro modal" not in html


# --- explain prose nomeia o centro -------------------------------------------

def test_explain_summary_names_the_modal_center():
    a = _analysis(
        key="D", mode="major", harmonic_analysis=[],
        modal_coloring={"flavor": "mixolydian", "evidence": ["bVII→I (1×)"], "where": [0]},
    )
    lines = render_summary(summarize_facts(a))
    assert any("D mixolídio" in ln for ln in lines)


# --- 3.3 anti-regressão de schema --------------------------------------------

def test_naming_does_not_mutate_canonical_fields():
    coloring = {"flavor": "mixolydian", "evidence": ["bVII→I (1×)"], "where": [0]}
    a = _analysis(modal_coloring=coloring)
    MarkdownReportGenerator()._generate_header(a, "http://yt")
    # O render não altera key/mode/modal_coloring — promoção é só de display.
    assert a["key"] == "D"
    assert a["mode"] == "major"
    assert a["modal_coloring"] is coloring
