"""cifra_core.theory — núcleo de teoria musical (Camada 1).

Classes de altura com ortografia preservada, intervalos, realização de
acordes em classes de altura e escalas/modos como dados.
"""

from cifra_core.theory.chord_realize import realize, root_pitch_class
from cifra_core.theory.pitch import (
    Note,
    interval_magnitude,
    interval_semitones,
)
from cifra_core.theory.scales import MODE_PATTERNS, build_scale

__all__ = [
    "MODE_PATTERNS",
    "Note",
    "build_scale",
    "interval_magnitude",
    "interval_semitones",
    "realize",
    "root_pitch_class",
]
