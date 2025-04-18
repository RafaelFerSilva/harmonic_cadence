import json
import os
import re
import unicodedata

import requests

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")


def cifra_slug(text: str) -> str:
    """
    Converte texto para o formato de URL do Cifra Club.

    Args:
        text: Texto a ser convertido (nome do artista ou música)

    Returns:
        str: Texto convertido para formato de URL
    """
    # Remove acentos
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Remove caracteres especiais, mantendo hífens
    text = re.sub(r"[^\w\s-]", "", text)

    # Lista de exceções (palavras que devem ser mantidas)
    keep_words = {"de", "do", "da", "dos", "das"}

    # Divide o texto em palavras
    words = text.lower().split()

    # Filtra mantendo palavras maiores que 2 letras ou que estejam na lista de exceções
    words = [w for w in words if len(w) > 2 or w in keep_words]

    # Junta as palavras com hífen
    return "-".join(words)


def get_cache_path(artist: str, song: str) -> str:
    """
    Gera o caminho do arquivo de cache para uma música.

    Args:
        artist: Nome do artista
        song: Nome da música

    Returns:
        str: Caminho completo do arquivo de cache
    """
    artist_slug = cifra_slug(artist)
    song_slug = cifra_slug(song)
    return os.path.join(DATA_DIR, f"{artist_slug}_{song_slug}.json")


def fetch_song_data(artist: str, song: str, use_local_fallback: bool = True) -> dict:
    artist_slug = cifra_slug(artist)
    song_slug = cifra_slug(song)
    local_path = get_cache_path(artist, song)

    try:
        url = f"http://localhost:3000/artists/{artist_slug}/songs/{song_slug}"
        response = requests.get(url)
        if response.status_code == 404:
            raise RuntimeError("Música não encontrada na API (404).")
        response.raise_for_status()
        data = response.json()
        if not data or "error" in data:
            raise RuntimeError("Música não encontrada na API.")
        # Salva cópia local
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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
        if not data or not data.get("cifra"):
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
