import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ChordQuality(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT = "dominant"
    HALF_DIMINISHED = "half-diminished"
    UNKNOWN = "unknown"


@dataclass
class ChordProperties:
    root: str
    quality: ChordQuality
    has_seventh: bool
    has_ninth: bool
    has_extension: bool
    bass: Optional[str] = None


class ChordPattern:
    """
    Utilitário para encontrar acordes em linhas de texto usando regex.
    """

    CHORD = re.compile(
        r"([A-G][#b]?"
        r"(?:m|maj|min|sus|dim|aug|add|M|°)?"
        r"(?:7|9|11|13)?"
        r"(?:\(.*?\))?"
        r"(?:/[A-G][#b]?)?)"
    )

    @classmethod
    def find_all(cls, text: str) -> List[str]:
        """Encontra todos os acordes em um texto."""
        return cls.CHORD.findall(text)


class Chord:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.properties = self._analyze_chord()

    def _analyze_chord(self) -> ChordProperties:
        root = self._extract_root()
        quality = self._determine_quality()
        has_seventh = "7" in self.symbol
        has_ninth = "9" in self.symbol
        has_extension = any(ext in self.symbol for ext in ["11", "13"])
        bass = self._extract_bass()
        return ChordProperties(
            root=root,
            quality=quality,
            has_seventh=has_seventh,
            has_ninth=has_ninth,
            has_extension=has_extension,
            bass=bass,
        )

    def _extract_root(self) -> str:
        match = re.match(r"^([A-G][#b]?)", self.symbol)
        return match.group(1) if match else ""

    def _determine_quality(self) -> ChordQuality:
        s = self.symbol.lower()
        if "m7b5" in s:
            return ChordQuality.HALF_DIMINISHED
        if "dim" in s or "°" in s:
            return ChordQuality.DIMINISHED
        if "aug" in s:
            return ChordQuality.AUGMENTED
        if "maj" in s or "M" in self.symbol:
            return ChordQuality.MAJOR
        if "m" in s and "maj" not in s:
            return ChordQuality.MINOR
        if "7" in s and "m" not in s and "maj" not in s:
            return ChordQuality.DOMINANT
        return ChordQuality.MAJOR  # default

    def _extract_bass(self) -> Optional[str]:
        match = re.search(r"/([A-G][#b]?)", self.symbol)
        return match.group(1) if match else None

    @property
    def root(self) -> str:
        return self.properties.root

    @property
    def quality(self) -> str:
        return self.properties.quality.value

    @property
    def is_minor(self) -> bool:
        return self.properties.quality == ChordQuality.MINOR

    @property
    def is_dominant_seventh(self) -> bool:
        return (
            self.properties.quality == ChordQuality.DOMINANT
            and self.properties.has_seventh
        )

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"Chord('{self.symbol}')"
