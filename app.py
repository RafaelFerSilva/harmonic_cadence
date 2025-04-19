from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
import unicodedata

app = Flask(__name__)

def clean_text(text):
    """
    Limpa o texto e normaliza caracteres especiais e acentos
    """
    text = text.strip()
    text = unicodedata.normalize('NFKD', text)
    text = unicodedata.normalize('NFC', text)
    return text

def decode_unicode_escape(text):
    """
    Decodifica sequências Unicode escape em texto legível
    """
    try:
        return bytes(text, 'utf-8').decode('unicode_escape')
    except Exception:
        return text

def is_tablature_line(line):
    """
    Identifica se uma linha é parte de uma tablatura
    """
    tab_pattern = re.compile(r'^[eEbBgGdDaA]\|[-0-9xX/\|\s]*\|?$')
    return bool(tab_pattern.match(line))

def is_chord_only_line(line):
    """
    Identifica se uma linha contém apenas acordes (um ou mais)
    """
    chord_pattern = re.compile(
        r'^([A-G][#b]?(?:m|maj|min|sus|dim|aug|add)?\d*(?:/[A-G][#b]?)?\s*)+$'
    )
    return bool(chord_pattern.match(line.strip()))

def is_section_marker(line):
    """
    Identifica se é uma linha de marcação de seção (ex: [Intro], [Refrão])
    """
    return line.strip().startswith('[') and line.strip().endswith(']')

def has_lyrics(line):
    """
    Verifica se a linha contém letra da música
    (tem caracteres além de acordes e símbolos musicais)
    """
    # Remove acordes e símbolos comuns
    chord_pattern = re.compile(r'[A-G][#b]?(?:m|maj|min|sus|dim|aug|add)?\d*(?:/[A-G][#b]?)?')
    cleaned = chord_pattern.sub('', line)
    # Remove símbolos musicais comuns
    cleaned = re.sub(r'[\(\)\[\]\/\-_\s]', '', cleaned)
    return bool(cleaned)

def should_keep_line(line):
    """
    Determina se uma linha deve ser mantida na cifra
    """
    ignore_patterns = [
        r'^tom:$',  # Remove linha "tom:"
        r'^Parte \d+ de \d+$',  # Remove "Parte X de Y"
        r'^[eEbBgGdDaA]\|[-0-9xX/\|\s]*\|?$',  # Remove linhas de tablatura
        r'^\s*$',  # Remove linhas vazias
    ]
    cleaned_line = line.strip()

    # Se a linha estiver vazia, ignorar
    if not cleaned_line:
        return False

    # Se corresponder a algum padrão para ignorar
    for pattern in ignore_patterns:
        if re.match(pattern, cleaned_line):
            return False

    # Se for apenas acordes sem letra, manter só se for marcador de seção
    if is_chord_only_line(cleaned_line) and not has_lyrics(cleaned_line):
        return is_section_marker(cleaned_line)

    return True

def process_cifra_line(line):
    """
    Processa uma linha da cifra, tratando acordes e texto
    """
    cleaned_line = clean_text(line)
    if not should_keep_line(cleaned_line):
        return None

    # Para linhas com letra, decodifica caracteres especiais
    return decode_unicode_escape(cleaned_line)

def clean_cifra_lines(lines):
    """
    Limpa e organiza as linhas da cifra, removendo redundâncias
    """
    cleaned_lines = []
    prev_line = None

    for line in lines:
        # Pula linhas vazias
        if not line or not line.strip():
            continue

        # Evita repetição de linhas idênticas consecutivas
        if line == prev_line:
            continue

        cleaned_lines.append(line)
        prev_line = line

    return cleaned_lines

def get_cifra(artist, song):
    url = f"https://www.cifraclub.com.br/{artist}/{song}/#tabs=false"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Charset': 'utf-8'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Extrair informações básicas
        title = soup.find('h1', {'class': 'g-header'})
        artist_name = soup.find('a', {'class': 'artist'})

        # Extrair a cifra
        cifra_div = soup.find('div', {'class': 'cifra_cnt'})
        if cifra_div:
            raw_lines = cifra_div.get_text().split('\n')
            processed_lines = [process_cifra_line(line) for line in raw_lines]
            cifra_lines = [line for line in processed_lines if line is not None and line.strip() != '']
            cifra_lines = clean_cifra_lines(cifra_lines)
        else:
            cifra_lines = []

        # Extrair link do YouTube se disponível
        youtube_link = ''
        video_element = soup.find('div', {'class': 'video-player'})
        if video_element:
            youtube_link = video_element.get('data-video-id', '')
            if youtube_link:
                youtube_link = f"https://www.youtube.com/watch?v={youtube_link}"

        processed_title = clean_text(title.text) if title else song
        processed_artist = clean_text(artist_name.text) if artist_name else artist

        return {
            'artist': processed_artist,
            'name': processed_title,
            'youtube_url': youtube_link,
            'cifraclub_url': url,
            'cifra': cifra_lines
        }

    except Exception as e:
        return {'error': str(e)}

@app.route('/artists/<artist>/songs/<song>')
def get_song(artist, song):
    artist = clean_text(artist)
    song = clean_text(song)
    result = get_cifra(artist, song)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response


def get_artist_songs(artist):
    """
    Obtém a lista de músicas de um artista do Cifra Club
    """
    url = f"https://www.cifraclub.com.br/{artist}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Charset': 'utf-8'
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        songs_list = []
        songs_container = soup.find('ul', {
            'class': 'list-links art_musics alf all artistMusics--allSongs',
            'id': 'js-a-songs'
        })

        if songs_container:
            for song_item in songs_container.find_all('li'):
                song_link = song_item.find('a')
                if song_link:
                    song_name = clean_text(song_link.text)
                    song_url = song_link.get('href', '')

                    # Verifica se é uma URL de letra
                    is_lyrics_only = '/letra/' in song_url.lower()

                    # Extrai o slug da URL
                    if is_lyrics_only:
                        # Caso seja URL com /letra/ e ID numérico
                        if re.search(r'/\d+/letra/', song_url):
                            song_slug = song_url.split('/')[-3]  # Pega o ID (ex: 925206)
                        else:
                            # URL do tipo /artista/nome-da-musica/letra/
                            song_slug = song_url.split('/')[-2]  # Pega o penúltimo elemento
                    else:
                        # URL normal /artista/nome-da-musica/
                        song_slug = song_url.rstrip('/').split('/')[-1]

                    songs_list.append({
                        'name': song_name,
                        'slug': song_slug,
                        'url': f"https://www.cifraclub.com.br{song_url}",
                        'only_lyrics': is_lyrics_only
                    })

        artist_name = soup.find('h1', {'class': 'artist-name'})
        artist_name = clean_text(artist_name.text) if artist_name else artist

        return {
            'artist': artist_name,
            'total_songs': len(songs_list),
            'songs': songs_list
        }

    except Exception as e:
        return {'error': str(e)}

@app.route('/artists/<artist>/songs')
def list_artist_songs(artist):
    """
    Endpoint para listar todas as músicas de um artista
    """
    artist = clean_text(artist)
    result = get_artist_songs(artist)
    response = jsonify(result)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'usage': '/artists/<artist>/songs/<song>',
        'example': '/artists/joao-gilberto/songs/chega-de-saudade'
    })
    
if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0', port=3000, debug=True)
