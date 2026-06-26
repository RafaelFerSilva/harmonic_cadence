class SongProviderError(Exception):
    """Base para todas as falhas de um SongProvider."""


class SongNotFound(SongProviderError):
    """A música não existe (ex.: HTTP 404 / scraper devolveu None)."""

    def __init__(self, artist: str, song: str):
        self.artist = artist
        self.song = song
        super().__init__(f"Música não encontrada: {artist} - {song}")


class ArtistNotFound(SongProviderError):
    """O artista não existe."""

    def __init__(self, artist: str):
        self.artist = artist
        super().__init__(f"Artista não encontrado: {artist}")


class EmptyCifra(SongProviderError):
    """A música existe mas não tem linhas de cifra (só letra/instrumental)."""

    def __init__(self, artist: str, song: str):
        self.artist = artist
        self.song = song
        super().__init__(f"Música sem cifra: {artist} - {song}")


class ProviderUnavailable(SongProviderError):
    """Falha transitória (conexão/timeout/5xx) — pode tentar cache ou retry."""


class UpstreamError(SongProviderError):
    """A origem respondeu, mas o conteúdo não pôde ser interpretado."""
