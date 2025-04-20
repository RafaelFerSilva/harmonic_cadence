import re
import requests
from bs4 import BeautifulSoup
from app.utils.encoding import fix_encoding

class CifraClubScraper:
    def scrape_cifra(self, artist: str, song: str) -> dict:
        url = f"https://www.cifraclub.com.br/{artist}/{song}/#tabs=false"
        response = requests.get(url, headers=self._get_headers())
        soup = BeautifulSoup(response.text, 'lxml')

        title = soup.find('h1', {'class': 'g-header'})
        artist_name = soup.find('a', {'class': 'artist'})
        cifra_div = soup.find('div', {'class': 'cifra_cnt'})
        youtube_link = self._get_youtube_link(soup)

        return {
            'artist': fix_encoding(artist_name.text.strip() if artist_name else artist),
            'title': fix_encoding(title.text.strip() if title else song),
            'cifra_div_text': cifra_div.get_text(separator='\n', strip=True) if cifra_div else '',
            'youtube_link': youtube_link,
            'url': url
        }

    def scrape_artist_songs(self, artist: str) -> list[dict]:
        url = f"https://www.cifraclub.com.br/{artist}"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        songs_container = soup.find('ul', {'id': 'js-a-songs'})
        songs = []
        if not songs_container:
            return []

        for song_item in songs_container.find_all('li'):
            song_link = song_item.find('a')
            if not song_link:
                continue

            song_url = song_link['href']
            is_lyrics = '/letra/' in song_url.lower()

            # Extração do slug com regex
            slug_match = re.search(r'(?<=/)\d+(?=/letra/|$)', song_url)
            song_slug = slug_match.group() if slug_match else song_url.split('/')[-1]

            songs.append({
                'name': fix_encoding(song_link.text.strip()),
                'slug': song_slug,
                'url': song_url,
                'only_lyrics': is_lyrics,
            })
        return songs

    def _get_youtube_link(self, soup: BeautifulSoup) -> str:
        video_element = soup.find('div', {'class': 'video-player'})
        if not video_element:
            return ''
        video_id = video_element.get('data-video-id', '')
        return f"https://www.youtube.com/watch?v={video_id}" if video_id else ''

    def _get_headers(self) -> dict:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Charset': 'utf-8'
        }
