"""Prova a decisão de DX: analisar via provider in-process, sem servidor HTTP."""

from cifra_core import Cifra
from cifra_scraper.song_provider import InProcessSongProvider
from harmonic_analysis.services.analysis_service import AnalysisService


class StubRepo:
    """Repositório falso — não toca a rede nem o servidor."""

    def get_cifra(self, artist, song):
        return Cifra(
            artist="Djavan",
            name="Sina",
            cifra=("C  Am  F  G", "C  G  C"),
        )

    def get_artist_songs(self, artist):
        return []


def test_in_process_analysis_runs_without_server():
    service = AnalysisService(InProcessSongProvider(StubRepo()))
    result = service.analyze_song_from_api("Djavan", "Sina")
    assert result["success"] is True
    assert result["key"] is not None
    assert "harmonic_analysis" in result
