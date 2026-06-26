import pytest
import requests

from cifra_core import (
    ArtistNotFound,
    Cifra,
    EmptyCifra,
    ProviderUnavailable,
    SongNotFound,
)
from cifra_scraper.song_provider import InProcessSongProvider


class FakeRepo:
    def __init__(self, cifra=None, exc=None, songs=None):
        self.cifra = cifra
        self.exc = exc
        self.songs = songs if songs is not None else []

    def get_cifra(self, artist, song):
        if self.exc:
            raise self.exc
        return self.cifra

    def get_artist_songs(self, artist):
        if self.exc:
            raise self.exc
        return self.songs


def test_none_maps_to_song_not_found():
    p = InProcessSongProvider(FakeRepo(cifra=None))
    with pytest.raises(SongNotFound):
        p.get_song("Djavan", "X")


def test_empty_maps_to_empty_cifra():
    p = InProcessSongProvider(FakeRepo(cifra=Cifra(artist="Djavan", name="Sina")))
    with pytest.raises(EmptyCifra):
        p.get_song("Djavan", "Sina")


def test_scrape_failure_maps_to_unavailable():
    p = InProcessSongProvider(
        FakeRepo(exc=requests.exceptions.ConnectionError("down"))
    )
    with pytest.raises(ProviderUnavailable):
        p.get_song("Djavan", "Sina")


def test_success_returns_cifra():
    c = Cifra(artist="Djavan", name="Sina", cifra=("C  Am",))
    p = InProcessSongProvider(FakeRepo(cifra=c))
    assert p.get_song("Djavan", "Sina") == c


def test_empty_artist_list_maps_to_not_found():
    p = InProcessSongProvider(FakeRepo(songs=[]))
    with pytest.raises(ArtistNotFound):
        p.list_artist_songs("Ninguem")
