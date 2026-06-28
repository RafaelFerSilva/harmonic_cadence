"""Regressão da Sina: A maior (termina em D/A) NÃO é lida como "D menor".

O bug histórico: a detecção automática de modo pegava a raiz do último acorde (D) e
classificava frígio de notas incidentais, sobrescrevendo o detect_key (A maior). A
promoção modal foi removida (ver change `fix-or-remove-church-mode`), então a leitura
tonal agora prevalece incondicionalmente — não há `modal_analysis`.
"""

from cifra_core.theory import Note

from harmonic_analysis.domain.modal import _central_pc
from harmonic_analysis.services.analysis_service import AnalysisService

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
    assert res["modal_analysis"] is None  # sem detecção modal automática
