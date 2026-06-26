from dataclasses import dataclass
from enum import Enum
from typing import Optional

from cifra_core.theory import parse as parse_chord


class ChordQuality(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT = "dominant"
    HALF_DIMINISHED = "half-diminished"
    SUSPENDED = "suspended"
    POWER = "power"
    UNKNOWN = "unknown"


@dataclass
class ChordProperties:
    root: str
    quality: ChordQuality
    has_seventh: bool
    has_ninth: bool
    has_extension: bool
    bass: Optional[str] = None


class Chord:
    """Acorde do domínio. Fase 1: deriva a qualidade/slots do parser estruturado
    de `cifra_core.theory` (fonte única), em vez de fazer sniffing de string.
    A API pública (`root`, `quality`, `is_minor`, `is_dominant_seventh`,
    `properties`) é preservada."""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.properties = self._analyze_chord()

    def _analyze_chord(self) -> ChordProperties:
        try:
            parsed = parse_chord(self.symbol)
        except Exception:
            return ChordProperties(
                root=self._fallback_root(),
                quality=ChordQuality.UNKNOWN,
                has_seventh=False,
                has_ninth=False,
                has_extension=False,
                bass=None,
            )
        return ChordProperties(
            root=str(parsed.root),
            quality=ChordQuality(parsed.category().value),
            has_seventh=parsed.seventh.value != "none",
            has_ninth="9" in self.symbol,
            has_extension=any(ext in self.symbol for ext in ["11", "13"]),
            bass=str(parsed.bass) if parsed.bass is not None else None,
        )

    def _fallback_root(self) -> str:
        import re

        match = re.match(r"^([A-G][#b]?)", self.symbol)
        return match.group(1) if match else ""

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
        return self.properties.quality == ChordQuality.DOMINANT

    def __str__(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return f"Chord('{self.symbol}')"
