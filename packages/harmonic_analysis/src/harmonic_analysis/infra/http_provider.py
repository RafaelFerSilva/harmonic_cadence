from typing import List

import requests

from cifra_core import (
    ArtistNotFound,
    Cifra,
    EmptyCifra,
    ProviderUnavailable,
    SongNotFound,
    SongRef,
    UpstreamError,
    slugify,
)


class HttpSongProvider:
    """Adaptador que obtém cifras do serviço Flask via HTTP."""

    def __init__(self, base_url: str = "http://localhost:3000", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get_json(self, url: str):
        try:
            resp = requests.get(url, timeout=self.timeout)
        except requests.exceptions.RequestException as e:
            raise ProviderUnavailable(f"API inacessível: {e}") from e
        if resp.status_code >= 500:
            raise ProviderUnavailable(f"API retornou {resp.status_code}")
        return resp

    def get_song(self, artist: str, song: str) -> Cifra:
        url = f"{self.base_url}/api/artists/{slugify(artist)}/songs/{slugify(song)}"
        resp = self._get_json(url)
        if resp.status_code == 404:
            raise SongNotFound(artist, song)
        try:
            resp.raise_for_status()
            data = resp.json()
        except ValueError as e:
            raise UpstreamError(f"Resposta inválida da API: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ProviderUnavailable(str(e)) from e
        if not data or "error" in data:
            raise SongNotFound(artist, song)
        cifra = Cifra.from_api(data)
        if cifra.is_empty:
            raise EmptyCifra(artist, song)
        return cifra

    def list_artist_songs(self, artist: str) -> List[SongRef]:
        url = f"{self.base_url}/api/artists/{slugify(artist)}/songs"
        resp = self._get_json(url)
        if resp.status_code == 404:
            raise ArtistNotFound(artist)
        try:
            resp.raise_for_status()
            data = resp.json()
        except ValueError as e:
            raise UpstreamError(f"Resposta inválida da API: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ProviderUnavailable(str(e)) from e
        if not data or "error" in data:
            raise ArtistNotFound(artist)
        return [SongRef.from_api(s) for s in data.get("songs", [])]
