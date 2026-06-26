import pytest
import requests

from cifra_core import (
    ArtistNotFound,
    EmptyCifra,
    ProviderUnavailable,
    SongNotFound,
    UpstreamError,
)
from harmonic_analysis.infra.http_provider import HttpSongProvider


class FakeResp:
    def __init__(self, status=200, json_data=None, raise_json=False):
        self.status_code = status
        self._json = json_data
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("bad json")
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(str(self.status_code))


def _patch(monkeypatch, resp=None, exc=None):
    def fake_get(url, timeout=None):
        if exc:
            raise exc
        return resp

    monkeypatch.setattr(
        "harmonic_analysis.infra.http_provider.requests.get", fake_get
    )


def test_404_maps_to_song_not_found(monkeypatch):
    _patch(monkeypatch, resp=FakeResp(404))
    with pytest.raises(SongNotFound):
        HttpSongProvider().get_song("Djavan", "X")


def test_connection_error_maps_to_unavailable(monkeypatch):
    _patch(monkeypatch, exc=requests.exceptions.ConnectionError("down"))
    with pytest.raises(ProviderUnavailable):
        HttpSongProvider().get_song("Djavan", "Sina")


def test_500_maps_to_unavailable(monkeypatch):
    _patch(monkeypatch, resp=FakeResp(500))
    with pytest.raises(ProviderUnavailable):
        HttpSongProvider().get_song("Djavan", "Sina")


def test_bad_body_maps_to_upstream_error(monkeypatch):
    _patch(monkeypatch, resp=FakeResp(200, raise_json=True))
    with pytest.raises(UpstreamError):
        HttpSongProvider().get_song("Djavan", "Sina")


def test_empty_cifra_maps_to_empty(monkeypatch):
    _patch(
        monkeypatch,
        resp=FakeResp(200, json_data={"artist": "Djavan", "name": "Sina", "cifra": []}),
    )
    with pytest.raises(EmptyCifra):
        HttpSongProvider().get_song("Djavan", "Sina")


def test_success_returns_cifra(monkeypatch):
    _patch(
        monkeypatch,
        resp=FakeResp(
            200, json_data={"artist": "Djavan", "name": "Sina", "cifra": ["C  Am"]}
        ),
    )
    c = HttpSongProvider().get_song("Djavan", "Sina")
    assert c.name == "Sina"
    assert c.cifra == ("C  Am",)


def test_list_404_maps_to_artist_not_found(monkeypatch):
    _patch(monkeypatch, resp=FakeResp(404))
    with pytest.raises(ArtistNotFound):
        HttpSongProvider().list_artist_songs("Ninguem")
