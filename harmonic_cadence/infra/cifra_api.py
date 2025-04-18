import requests


def fetch_song_data(artist: str, song: str) -> dict:
    """
    Busca os dados da música na API local.
    """
    url = f"http://localhost:3000/artists/{artist}/songs/{song}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
