from cifra_core import Cifra, SongRef, clean_cifra_lines, clean_text

from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper


class CifraClubRepository:
    def __init__(self, scraper: CifraClubScraper):
        self.scraper = scraper

    def get_cifra(self, artist: str, song: str) -> Cifra | None:
        raw_data = self.scraper.scrape_cifra(artist, song)
        if not raw_data:
            return None

        # Filtragem canônica de linhas (cifra_core) — fonte única, idempotente.
        raw_lines = raw_data.get("cifra_div_text", "").split("\n")
        cifra_lines = clean_cifra_lines(raw_lines)

        return Cifra(
            artist=raw_data["artist"],
            name=raw_data["title"],
            cifra=tuple(cifra_lines),
            cifra_html=raw_data.get("cifra_html", ""),
            youtube_url=raw_data["youtube_link"],
            cifraclub_url=raw_data["url"],
        )

    def get_artist_songs(self, artist: str) -> list[dict]:
        raw_songs = self.scraper.scrape_artist_songs(artist)
        songs: list[dict] = []
        for song in raw_songs:
            if not song.get("name"):
                continue  # Ignora músicas sem nome
            ref = SongRef(
                name=clean_text(song["name"]),
                slug=song.get("slug", ""),
                url=f'https://www.cifraclub.com.br{song["url"]}',
                only_lyrics=song["only_lyrics"],
            )
            songs.append(ref.to_dict())
        return songs
