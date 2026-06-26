"""URLs do Cifra Club são slugificadas (regressão: nomes crus davam 404)."""

import cifra_scraper.infrastructure.scrapers.cifraclub_scraper as scraper_mod
from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper


class _FakeResponse:
    def __init__(self, text=""):
        self.text = text

    def raise_for_status(self):
        return None


def _capture_get(monkeypatch):
    """Substitui requests.get capturando a URL, sem ir à rede."""
    captured = {}

    def fake_get(url, headers=None, **kwargs):
        captured["url"] = url
        return _FakeResponse("<html></html>")

    monkeypatch.setattr(scraper_mod.requests, "get", fake_get)
    return captured


def test_scrape_cifra_slugifies_artist_and_song(monkeypatch):
    captured = _capture_get(monkeypatch)
    CifraClubScraper().scrape_cifra("Djavan", "Oceano")
    assert captured["url"].startswith("https://www.cifraclub.com.br/djavan/oceano/")


def test_scrape_cifra_handles_accents_and_spaces(monkeypatch):
    captured = _capture_get(monkeypatch)
    CifraClubScraper().scrape_cifra("Tom Jobim", "Águas de Março")
    assert "/tom-jobim/aguas-de-marco/" in captured["url"]


def test_scrape_artist_songs_slugifies_artist(monkeypatch):
    captured = _capture_get(monkeypatch)
    CifraClubScraper().scrape_artist_songs("Tom Jobim")
    assert captured["url"] == "https://www.cifraclub.com.br/tom-jobim/"


def test_slug_is_idempotent_for_already_slugged_input(monkeypatch):
    captured = _capture_get(monkeypatch)
    CifraClubScraper().scrape_cifra("djavan", "oceano")
    assert captured["url"].startswith("https://www.cifraclub.com.br/djavan/oceano/")
