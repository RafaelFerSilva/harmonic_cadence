"""Extração do tom (#cifra_tom) do Cifra Club."""

from bs4 import BeautifulSoup

from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper


def _soup(html):
    return BeautifulSoup(html, "html.parser")


def test_extract_tom_major():
    s = CifraClubScraper()
    assert s._extract_tom(_soup('<div id="cifra_tom">Tom: <a>G</a></div>')) == "G"


def test_extract_tom_minor_and_accidentals():
    s = CifraClubScraper()
    assert s._extract_tom(_soup('<div id="cifra_tom">Tom: Am</div>')) == "Am"
    assert s._extract_tom(_soup('<div id="cifra_tom">Tom: F#m</div>')) == "F#m"
    assert s._extract_tom(_soup('<div id="cifra_tom">Tom: Bb</div>')) == "Bb"


def test_extract_tom_absent_is_empty():
    s = CifraClubScraper()
    assert s._extract_tom(_soup("<div>sem elemento de tom</div>")) == ""
