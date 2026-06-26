from typing import List, Optional

import requests

from cifra_core import (
    ArtistNotFound,
    Cifra,
    EmptyCifra,
    ProviderUnavailable,
    SongNotFound,
    SongRef,
    UpstreamError,
)

from cifra_scraper.infrastructure.repositories.cifraclub import CifraClubRepository
from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper


class InProcessSongProvider:
    """Adaptador que raspa o Cifra Club no próprio processo (sem subir o servidor)."""

    def __init__(self, repository: Optional[CifraClubRepository] = None):
        self.repository = repository or CifraClubRepository(CifraClubScraper())

    def get_song(self, artist: str, song: str) -> Cifra:
        try:
            cifra = self.repository.get_cifra(artist, song)
        except requests.exceptions.RequestException as e:
            raise ProviderUnavailable(f"Falha ao raspar a origem: {e}") from e
        except Exception as e:  # noqa: BLE001 - mapeia falha inesperada de parse
            raise UpstreamError(f"Erro inesperado no scraping: {e}") from e
        if cifra is None:
            raise SongNotFound(artist, song)
        if cifra.is_empty:
            raise EmptyCifra(artist, song)
        return cifra

    def list_artist_songs(self, artist: str) -> List[SongRef]:
        try:
            songs = self.repository.get_artist_songs(artist)
        except requests.exceptions.RequestException as e:
            raise ProviderUnavailable(f"Falha ao raspar a origem: {e}") from e
        except Exception as e:  # noqa: BLE001
            raise UpstreamError(f"Erro inesperado no scraping: {e}") from e
        if not songs:
            raise ArtistNotFound(artist)
        return [SongRef.from_api(s) for s in songs]
