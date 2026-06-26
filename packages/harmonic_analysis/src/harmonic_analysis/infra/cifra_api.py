import json
import os

import requests

from cifra_core import slugify

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")


def get_cache_path(artist: str, song: str) -> str:
    """
    Gera o caminho do arquivo de cache para uma música.

    Args:
        artist: Nome do artista
        song: Nome da música

    Returns:
        str: Caminho completo do arquivo de cache
    """
    artist_slug = slugify(artist)
    song_slug = slugify(song)
    return os.path.join(DATA_DIR, f"{artist_slug}_{song_slug}.json")


def fetch_song_data(artist: str, song: str, use_local_fallback: bool = True) -> dict:
    artist_slug = slugify(artist)
    song_slug = slugify(song)
    local_path = get_cache_path(artist, song)

    try:
        url = f"http://localhost:3000/api/artists/{artist_slug}/songs/{song_slug}"
        response = requests.get(url)
        if response.status_code == 404:
            raise RuntimeError("Música não encontrada na API (404).")
        response.raise_for_status()
        data = response.json()

        if not data or "error" in data or data is None:
            raise RuntimeError("Música não encontrada na API.")

        return data

    except requests.exceptions.ConnectionError:
        if use_local_fallback and os.path.exists(local_path):
            print("API offline. Usando dados locais salvos anteriormente.")
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise RuntimeError(
                "API offline e dados locais não encontrados. "
                "Não é possível continuar a análise."
            )
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados da música: {e}")


def download_and_cache_song(artist: str, song: str, force: bool = False) -> bool:
    """
    Baixa e salva os dados da música para uso offline.

    Args:
        artist: Nome do artista
        song: Nome da música
        force: Se True, força o download mesmo se já existir no cache

    Returns:
        bool: True se o download foi bem sucedido, False caso contrário
    """
    local_path = get_cache_path(artist, song)

    # Verifica cache existente
    if os.path.exists(local_path) and not force:
        print(f"Cache já existe para: {artist} - {song}")
        return True

    try:
        # Busca dados da API (sem usar cache)
        data = fetch_song_data(artist, song, use_local_fallback=False)

        # Valida se os dados são válidos
        if not data or data is None or not data["cifra"] or data["cifra"] == []:
            raise RuntimeError("Dados da música inválidos ou vazios")

        # Salva no cache
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Cache salvo com sucesso: {artist} - {song}")
        return True

    except Exception as e:
        print(f"Erro ao baixar {artist} - {song}: {e}")
        return False


def fetch_artist_songs(artist: str) -> dict:
    """
    Busca a lista completa de músicas de um artista da API.

    Args:
        artist: Nome do artista

    Returns:
        dict: Dados do artista e lista de músicas
    """
    artist_slug = slugify(artist)
    try:
        url = f"http://localhost:3000/api/artists/{artist_slug}/songs"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data or "error" in data:
            raise RuntimeError("Artista não encontrado na API.")
        return data
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar lista de músicas do artista: {e}")


def get_artist_cache_path(artist: str) -> str:
    """
    Gera o caminho do arquivo de cache para a lista de músicas do artista.

    Args:
        artist: Nome do artista

    Returns:
        str: Caminho completo do arquivo de cache
    """
    artist_slug = slugify(artist)
    return os.path.join(DATA_DIR, f"{artist_slug}_songs.json")


def cache_all_artist_songs(artist: str, force: bool = False) -> tuple[int, int]:
    """
    Baixa e salva todas as músicas de um artista para uso offline.

    Args:
        artist: Nome do artista
        force: Se True, força o download mesmo se já existir no cache

    Returns:
        tuple: (total de músicas, número de músicas baixadas com sucesso)
    """
    # Primeiro, busca a lista de músicas do artista
    try:
        artist_data = fetch_artist_songs(artist)
    except Exception as e:
        print(f"Erro ao buscar lista de músicas do artista: {e}")
        return 0, 0

    # Salva a lista de músicas do artista
    artist_cache_path = get_artist_cache_path(artist)
    os.makedirs(os.path.dirname(artist_cache_path), exist_ok=True)
    with open(artist_cache_path, "w", encoding="utf-8") as f:
        json.dump(artist_data, f, ensure_ascii=False, indent=2)

    total_songs = len(artist_data["songs"])
    successful_downloads = 0

    print(f"\nBaixando {total_songs} músicas de {artist}...")

    # Download cada música individualmente
    for i, song in enumerate(artist_data["songs"], 1):
        song_name = song["name"]
        print(f"\nProcessando ({i}/{total_songs}): {song_name}")

        try:
            if not song["only_lyrics"]:
                if download_and_cache_song(artist, song_name, force):
                    successful_downloads += 1
        except Exception as e:
            print(f"Erro ao baixar {song_name}: {e}")
            continue

    print(
        f"\nDownload concluído: {successful_downloads}/{total_songs} músicas baixadas com sucesso"
    )
    return total_songs, successful_downloads


def load_artist_songs(artist: str) -> list[str]:
    """
    Carrega a lista de músicas do artista do cache.

    Args:
        artist: Nome do artista

    Returns:
        list: Lista com os nomes das músicas
    """
    cache_path = get_artist_cache_path(artist)
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [song["name"] for song in data["songs"]]
    except FileNotFoundError:
        raise RuntimeError(f"Cache não encontrado para o artista: {artist}")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar cache do artista: {e}")
