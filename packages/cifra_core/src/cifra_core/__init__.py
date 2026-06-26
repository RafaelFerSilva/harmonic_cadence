"""cifra_core — shared core for the harmonic_cadence monorepo.

Single source of truth for encoding correction, cifra line filtering,
chord detection, the Cifra/SongRef models, and the SongProvider port.
"""

from cifra_core.chords import ChordPattern
from cifra_core.encoding import fix_encoding
from cifra_core.lines import clean_cifra_lines, clean_text, decode_unicode_escape
from cifra_core.models import Cifra, SongRef
from cifra_core.slug import slugify

__version__ = "0.1.0"

__all__ = [
    "ChordPattern",
    "Cifra",
    "SongRef",
    "clean_cifra_lines",
    "clean_text",
    "decode_unicode_escape",
    "fix_encoding",
    "slugify",
]
