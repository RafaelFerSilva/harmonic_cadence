
class Cifra:
    def __init__(self, artist, name, youtube_url, cifraclub_url, cifra):
        self.artist = artist
        self.name = name
        self.youtube_url = youtube_url
        self.cifraclub_url = cifraclub_url
        self.cifra = cifra
    
    def to_dict(self):
        return {
            'artist': self.artist,
            'name': self.name,
            'youtube_url': self.youtube_url,
            'cifraclub_url': self.cifraclub_url,
            'cifra': self.cifra
        }

