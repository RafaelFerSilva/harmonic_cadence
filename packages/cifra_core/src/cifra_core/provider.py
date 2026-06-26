from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from cifra_core.models import Cifra, SongRef


@runtime_checkable
class SongProvider(Protocol):
    """Porta pela qual o analisador obtém cifras e listagens de músicas.

    Adaptadores recebem nomes humanos e fazem o slugify internamente.
    """

    def get_song(self, artist: str, song: str) -> Cifra:
        """Retorna a Cifra (linhas já limpas).

        Raises:
            SongNotFound | ArtistNotFound | EmptyCifra
            | ProviderUnavailable | UpstreamError
        """
        ...

    def list_artist_songs(self, artist: str) -> List[SongRef]:
        """Raises: ArtistNotFound | ProviderUnavailable | UpstreamError."""
        ...
