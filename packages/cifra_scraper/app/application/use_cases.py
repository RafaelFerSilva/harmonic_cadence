from app.domain.entities import Cifra
from app.infrastructure.repositories.cifraclub import CifraClubRepository

class GetSongUseCase:
    def __init__(self, repository: CifraClubRepository):
        self.repository = repository

    def execute(self, artist: str, song: str) -> Cifra | None:
        return self.repository.get_cifra(artist, song)

class ListArtistSongsUseCase:
    def __init__(self, repository: CifraClubRepository):
        self.repository = repository

    def execute(self, artist: str) -> list[dict]:
        return self.repository.get_artist_songs(artist)