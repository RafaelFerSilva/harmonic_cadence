import json
from cifra_scraper.domain.entities import Cifra
from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper
from cifra_scraper.domain.cifra_utils import clean_cifra_lines, process_cifra_line, clean_text

class CifraClubRepository:
    def __init__(self, scraper: CifraClubScraper):
        self.scraper = scraper

    def get_cifra(self, artist: str, song: str) -> Cifra | None:
        raw_data = self.scraper.scrape_cifra(artist, song)
        if not raw_data:
            return None

        # Processa as linhas usando as funções do domínio
        raw_lines = raw_data.get('cifra_div_text', '').split('\n')
        processed_lines = [process_cifra_line(line) for line in raw_lines]
        cifra_lines = [
            line for line in processed_lines if line is not None and line.strip()
        ]
        cifra_lines = clean_cifra_lines(cifra_lines)
        cifra_html = raw_data.get('cifra_html', '')

        return Cifra(
            artist=raw_data['artist'],
            name=raw_data['title'],
            youtube_url=raw_data['youtube_link'],
            cifraclub_url=raw_data['url'],
            cifra=cifra_lines if cifra_lines else None,
            cifra_html=cifra_html
        )

    def get_artist_songs(self, artist: str) -> list[dict]:
      raw_songs = self.scraper.scrape_artist_songs(artist)
      processed_songs = []

      for song in raw_songs:
          if not song.get('name'):
              continue  # Ignora músicas sem nome

          processed_song = {
              'name': clean_text(song['name']),
              'slug': song.get('slug', ''),
              'url': f'https://www.cifraclub.com.br{song["url"]}',
              'only_lyrics': song['only_lyrics']
          }
          processed_songs.append(processed_song)

      return processed_songs