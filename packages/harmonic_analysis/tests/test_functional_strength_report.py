"""Qualidade funcional (forte/meio-forte/fraco) fiada na saída da análise."""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis
from harmonic_analysis.presentation.reports.markdown import MarkdownReportGenerator
from harmonic_analysis.services.analysis_service import AnalysisService


def _rows():
    svc = AnalysisService(None)
    H = HarmonicAnalysis("C", "major")
    chords = [Chord(s) for s in ["C", "F", "G7", "Em"]]
    return svc._detailed_harmonic_analysis(H, chords)


def test_detailed_analysis_carries_strength():
    by = {r["chord"]: r.get("strength") for r in _rows()}
    assert by["C"] == "strong"    # I  (principal)
    assert by["F"] == "strong"    # IV (principal)
    assert by["G7"] == "strong"   # V  (principal)
    assert by["Em"] == "weak"     # iii (substituto do I)


def test_markdown_renders_strength_column():
    md = MarkdownReportGenerator()._generate_harmonic_analysis({"harmonic_analysis": _rows()})
    assert "Força" in md
    assert "strong" in md
