"""Integração: provider → detecção de tonalidade → grau → função → relatório."""

from cifra_core import Cifra
from cifra_scraper.song_provider import InProcessSongProvider
from harmonic_analysis.services.analysis_service import AnalysisService


class StubRepo:
    def get_cifra(self, artist, song):
        # Dó maior com dominantes aplicados: E7→Am (V7/vi), D7→G (V7/V).
        return Cifra(
            artist="Teste",
            name="Progressão",
            cifra=("C  Am  Dm  G7  C", "E7  Am  D7  G7  C"),
        )

    def get_artist_songs(self, artist):
        return []


def test_full_path_detects_key_and_applied_dominants():
    service = AnalysisService(InProcessSongProvider(StubRepo()))
    result = service.analyze_song_from_api("Teste", "Progressão")

    assert result["success"] is True
    assert result["key"] == "C"
    assert result["mode"] == "major"

    codes = {entry.get("function_code") for entry in result["harmonic_analysis"]}
    assert "Dsec" in codes          # dominantes secundários reconhecidos
    assert "D" in codes             # dominante primário (G7→C)

    # caminho completo presente
    assert result["analysis_progression"]
    assert "cadences" in result
    assert "tonal_regions" in result
    assert len(result["tonal_regions"]) >= 1
