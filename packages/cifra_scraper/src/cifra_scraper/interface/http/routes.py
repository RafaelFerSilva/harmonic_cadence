from flask import Blueprint, jsonify
from cifra_scraper.application.use_cases import GetSongUseCase, ListArtistSongsUseCase
from cifra_scraper.infrastructure.repositories.cifraclub import CifraClubRepository
from cifra_scraper.infrastructure.scrapers.cifraclub_scraper import CifraClubScraper

bp = Blueprint('api', __name__)

@bp.route('/artists/<artist>/songs')
def list_artist_songs(artist: str):
    scraper = CifraClubScraper()
    repository = CifraClubRepository(scraper)
    use_case = ListArtistSongsUseCase(repository)
    songs = use_case.execute(artist)

    response = jsonify({'songs': songs})
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Cache-Control'] = 'no-cache'
    return response

@bp.route('/artists/<artist>/songs/<song>')
def get_song(artist: str, song: str):
    scraper = CifraClubScraper()
    repository = CifraClubRepository(scraper)
    use_case = GetSongUseCase(repository)
    cifra = use_case.execute(artist, song)
    
    return jsonify(cifra.to_dict()) if cifra else jsonify({'error': 'Cifra não encontrada'})