"""Localização PT-BR na apresentação (rótulos + render)."""

from harmonic_analysis.presentation.labels import (
    church_mode_pt,
    mode_pt,
    quality_pt,
    scale_pt,
)
from harmonic_analysis.presentation.reports.markdown import MarkdownReportGenerator


def test_mode_and_church_mode_labels():
    assert mode_pt("minor") == "menor"
    assert mode_pt("major") == "maior"
    assert church_mode_pt("phrygian") == "frígio"
    assert church_mode_pt("mixolydian") == "mixolídio"
    assert church_mode_pt("dorian") == "dórico"


def test_quality_labels():
    assert quality_pt("dominant") == "dominante"
    assert quality_pt("diminished") == "diminuto"
    assert quality_pt("half-diminished") == "meio-diminuto"
    assert quality_pt("suspended") == "suspenso"


def test_scale_labels_keep_the_root_letter():
    assert scale_pt("G mixolydian") == "G mixolídio"
    assert scale_pt("G lydian_dominant") == "G lídio b7"
    assert scale_pt("G diminished") == "G diminuta"   # escala (feminino)
    assert scale_pt("C ionian") == "C jônico"


def test_markdown_renders_quality_in_portuguese():
    rows = [
        {
            "chord": "G7", "degree": "V", "quality": "dominant",
            "strength": "strong", "function": "Dominante",
            "function_code": "D", "function_description": "tensão",
        }
    ]
    md = MarkdownReportGenerator()._generate_harmonic_analysis(
        {"harmonic_analysis": rows}
    )
    assert "dominante" in md
