"""Integração da Camada 2: modal, RNA, condução de vozes e escala-acorde."""

from cifra_core import Cifra
from cifra_scraper.song_provider import InProcessSongProvider
from harmonic_analysis.services.analysis_service import AnalysisService


class TonalStub:
    def get_cifra(self, artist, song):
        return Cifra(
            artist="T",
            name="Tonal",
            cifra=("C  C/E  F  G7/B", "Am  Dm7  G7  Cmaj7"),
        )

    def get_artist_songs(self, artist):
        return []


class ModalStub:
    def get_cifra(self, artist, song):
        return Cifra(artist="T", name="Modal", cifra=("G  F  C  G", "G  F  C  G"))

    def get_artist_songs(self, artist):
        return []


def _analyze(stub, name):
    return AnalysisService(InProcessSongProvider(stub)).analyze_song_from_api("T", name)


def test_tier2_sections_present_for_tonal_piece():
    r = _analyze(TonalStub(), "Tonal")
    assert r["success"] is True
    assert r["modal_analysis"] is None
    # RNA com inversões
    assert "I6" in r["roman_numerals"]
    assert "V6/5" in r["roman_numerals"]
    # condução de vozes: o baixo do C/E é E
    assert r["voice_leading"]["bass_line"][1] == "E"
    # escala-acorde
    scales = {cs["scale"] for cs in r["chord_scales"]}
    assert any("ionian" in s for s in scales)
    assert any("dorian" in s for s in scales)


def test_tier2_modal_piece_uses_modal_function():
    r = _analyze(ModalStub(), "Modal")
    assert r["success"] is True
    assert r["modal_analysis"] is not None
    assert r["modal_analysis"]["mode"] == "mixolydian"
    codes = {e.get("function_code") for e in r["harmonic_analysis"]}
    assert "Modal" in codes      # bVII é função modal
    assert "Emp" not in codes    # ...e não empréstimo
