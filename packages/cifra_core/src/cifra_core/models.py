from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class Cifra:
    """Contrato tipado de uma música. Imutável e seguro entre threads."""

    artist: str
    name: str
    cifra: tuple[str, ...] = ()
    cifra_html: str = ""
    youtube_url: str = ""
    cifraclub_url: str = ""

    @property
    def is_empty(self) -> bool:
        """True quando não há linhas de cifra (só letra / instrumental)."""
        return not self.cifra

    @classmethod
    def from_api(cls, d: Mapping[str, Any]) -> "Cifra":
        """Constrói a partir de um dict (resposta HTTP ou cache)."""
        lines = d.get("cifra") or ()
        return cls(
            artist=d.get("artist", "") or "",
            name=d.get("name", "") or "",
            cifra=tuple(lines),
            cifra_html=d.get("cifra_html", "") or "",
            youtube_url=d.get("youtube_url", "") or "",
            cifraclub_url=d.get("cifraclub_url", "") or "",
        )

    def to_dict(self) -> dict:
        return {
            "artist": self.artist,
            "name": self.name,
            "cifra": list(self.cifra),
            "cifra_html": self.cifra_html,
            "youtube_url": self.youtube_url,
            "cifraclub_url": self.cifraclub_url,
        }


@dataclass(frozen=True, slots=True)
class SongRef:
    """Entrada de listagem de músicas de um artista."""

    name: str
    slug: str
    url: str
    only_lyrics: bool = False

    @classmethod
    def from_api(cls, d: Mapping[str, Any]) -> "SongRef":
        return cls(
            name=d.get("name", "") or "",
            slug=d.get("slug", "") or "",
            url=d.get("url", "") or "",
            only_lyrics=bool(d.get("only_lyrics", False)),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "slug": self.slug,
            "url": self.url,
            "only_lyrics": self.only_lyrics,
        }
