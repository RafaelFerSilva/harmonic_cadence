"""Arbitragem tonalidade × modo: um modo só refina, nunca inverte (a Sina).

Regressão do bug reportado: a Sina (A maior, termina em D/A) era lida como
"D menor" porque detect_mode pegava a raiz do último acorde (D) e classificava
frígio de notas incidentais, sobrescrevendo o detect_key (A maior).
"""

from cifra_core.theory import Note

from harmonic_analysis.domain.modal import ModeInfo, _central_pc
from harmonic_analysis.services.analysis_service import (
    AnalysisService,
    _mode_refines_key,
)

# Progressão representativa da Sina: A maior, pedal de Lá, termina em D/A;
# G#m7 traz o D# que antes disparava "frígio".
SINA_LIKE = ["A", "D/A", "A", "D/A", "F#m7", "C#7(9-)", "C#m7", "G#m7(11)",
             "D7M", "A", "D/A"]


def test_central_tonic_is_the_bass_pedal_not_the_last_root():
    # A domina o baixo (pedal); D/A não deve fazer o centro virar Ré.
    assert _central_pc(SINA_LIKE) == Note.parse("A").pitch_class


def test_sina_like_is_read_as_a_major_not_d_minor():
    res = AnalysisService(None).analyze_song_data_structured(
        {"name": "x", "artist": "y", "cifra": ["   ".join(SINA_LIKE)]}
    )
    assert res["success"]
    assert res["key"] == "A"
    assert res["mode"] == "major"
    assert res["modal_analysis"] is None  # não é modal


def test_mode_must_match_tonic_and_quality_to_refine():
    # qualidade discorda (tom maior, modo menor) → rejeita
    assert not _mode_refines_key(ModeInfo(2, "D", "phrygian"), "D", "major")
    # tônica discorda → rejeita
    assert not _mode_refines_key(ModeInfo(2, "D", "phrygian"), "A", "minor")
    # tônica e qualidade concordam → aceita (refinamento genuíno)
    assert _mode_refines_key(ModeInfo(9, "A", "phrygian"), "A", "minor")
    # modo maior sobre tom maior, mesma tônica → aceita
    assert _mode_refines_key(ModeInfo(7, "G", "mixolydian"), "G", "major")
