
class Cifra:
    def __init__(
        self,
        artist: str,
        name: str,
        youtube_url: str,
        cifraclub_url: str,
        cifra: list[str],  
        cifra_html: str,   
    ):
        self.artist = artist
        self.name = name
        self.youtube_url = youtube_url
        self.cifraclub_url = cifraclub_url
        self.cifra = cifra
        self.cifra_html = cifra_html
    
    def to_dict(self):
        return {
            'artist': self.artist,
            'name': self.name,
            'youtube_url': self.youtube_url,
            'cifraclub_url': self.cifraclub_url,
            'cifra': self.cifra,
            'cifra_html': self.cifra_html
        }

