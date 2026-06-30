"""II cadencial primário / secundário / auxiliar — Chediak XIX, p.100.

Um acorde menor separado do dominante por 4ªJ ascendente (ii→V) é um II cadencial — DESDE QUE
o dominante RESOLVA no seu alvo (um dominante só funciona quando resolve 4ªJ descendente). O tipo
vem do alvo do dominante (5ª justa abaixo da sua fundamental): tônica = primário, grau diatônico
= secundário, empréstimo modal = auxiliar. A validade (resolução) é decidida pelo pré-passe
`ii_cadential_indices`, que precisa da progressão inteira (o next-next confirma a resolução).
"""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis


def _fn(key, seq, idx):
    """Analisa `seq[idx]` no contexto da progressão inteira `seq` (com os flags do pré-passe)."""
    h = HarmonicAnalysis(key, "major")
    chords = [Chord(s) for s in seq]
    ii = HarmonicAnalysis.ii_cadential_indices(chords)
    subv = HarmonicAnalysis.subv_extended_indices(chords)
    prev = chords[idx - 1] if idx > 0 else None
    nxt = chords[idx + 1] if idx < len(chords) - 1 else None
    return h.analyze_function(chords[idx], prev, nxt, idx in subv, idx in ii)


def test_primary_ii_cadential():
    code, name, _ = _fn("C", ["Dm7", "G7", "C"], 0)  # G7 resolve em C
    assert code == "D2"
    assert "primário" in name


def test_secondary_ii_cadential_of_iii():
    code, name, _ = _fn("C", ["F#m7", "B7", "Em"], 0)  # B7 resolve em Em
    assert code == "D2"
    assert "secundário" in name and "V7/III" in name


def test_secondary_ii_cadential_of_v():
    code, name, _ = _fn("C", ["Am7", "D7", "G"], 0)  # D7 resolve em G
    assert code == "D2"
    assert "secundário" in name and "V7/V" in name


def test_auxiliary_ii_cadential_of_bvii():
    code, name, _ = _fn("C", ["Cm7", "F7", "Bb"], 0)  # F7 resolve em Bb
    assert code == "D2"
    assert "auxiliar" in name and "V7/bVII" in name


def test_auxiliary_ii_cadential_of_bvi():
    code, name, _ = _fn("C", ["Bbm7", "Eb7", "Ab"], 0)  # Eb7 resolve em Ab
    assert code == "D2"
    assert "auxiliar" in name and "V7/bVI" in name


def test_secondary_ii_cadential_resolving_into_another_dominant():
    # Em7 A7 D7: A7 resolve em D (raiz), mesmo D7 sendo dominante (cadeia). É D2 secundário.
    code, name, _ = _fn("C", ["Em7", "A7", "D7"], 0)
    assert code == "D2"
    assert "secundário" in name


def test_secondary_ii_cadential_is_not_modal_borrowing():
    assert _fn("C", ["F#m7", "B7", "Em"], 0)[0] != "Emp"


def test_minor_before_non_resolving_dominant_is_not_ii_cadential():
    # Dm7 G7 Dm7: G7 NÃO resolve em C (volta a Dm7) — over-attribution antiga. Não é D2.
    code, _, _ = _fn("C", ["Dm7", "G7", "Dm7"], 0)
    assert code != "D2"


def test_minor_without_fourth_above_dominant_is_not_ii_cadential():
    # Dm7 → C (não há dominante 4ªJ acima): segue função subdominante, não II cadencial.
    code, _, _ = _fn("C", ["Dm7", "C", "G7"], 0)
    assert code != "D2"


def test_minor_followed_by_non_dominant_is_not_ii_cadential():
    # Dm7 → Em7 (próximo não é dominante): não é II cadencial.
    assert _fn("C", ["Dm7", "Em7", "Am7"], 0)[0] != "D2"
