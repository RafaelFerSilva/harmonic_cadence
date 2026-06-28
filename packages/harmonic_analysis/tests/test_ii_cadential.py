"""II cadencial primário / secundário / auxiliar — Chediak XIX, p.100.

Um acorde menor separado do dominante por 4ªJ ascendente (ii→V) é um II cadencial;
o tipo vem do alvo do dominante (5ª justa abaixo da sua fundamental): tônica =
primário, grau diatônico = secundário, empréstimo modal = auxiliar.
"""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis


def _fn(key, prev, sym, nxt):
    h = HarmonicAnalysis(key, "major")
    return h.analyze_function(
        Chord(sym), Chord(prev) if prev else None, Chord(nxt) if nxt else None
    )


def test_primary_ii_cadential():
    code, name, _ = _fn("C", "C", "Dm7", "G7")
    assert code == "D2"
    assert "primário" in name


def test_secondary_ii_cadential_of_iii():
    code, name, _ = _fn("C", "Em", "F#m7", "B7")
    assert code == "D2"
    assert "secundário" in name and "V7/III" in name


def test_secondary_ii_cadential_of_v():
    code, name, _ = _fn("C", "Em", "Am7", "D7")
    assert code == "D2"
    assert "secundário" in name and "V7/V" in name


def test_auxiliary_ii_cadential_of_bvii():
    code, name, _ = _fn("C", "C", "Cm7", "F7")
    assert code == "D2"
    assert "auxiliar" in name and "V7/bVII" in name


def test_auxiliary_ii_cadential_of_bvi():
    code, name, _ = _fn("C", "C", "Bbm7", "Eb7")
    assert code == "D2"
    assert "auxiliar" in name and "V7/bVI" in name


def test_secondary_ii_cadential_is_not_modal_borrowing():
    # F#m7 antes de B7 NÃO é empréstimo modal (era o bug).
    assert _fn("C", "Em", "F#m7", "B7")[0] != "Emp"


def test_minor_without_fourth_above_dominant_is_not_ii_cadential():
    # Dm7 → C (não há dominante 4ªJ acima): segue função subdominante, não II cadencial.
    code, _, _ = _fn("C", "C", "Dm7", "C")
    assert code != "D2"


def test_minor_followed_by_non_dominant_is_not_ii_cadential():
    # Dm7 → Em7 (próximo não é dominante): não é II cadencial.
    assert _fn("C", "C", "Dm7", "Em7")[0] != "D2"
