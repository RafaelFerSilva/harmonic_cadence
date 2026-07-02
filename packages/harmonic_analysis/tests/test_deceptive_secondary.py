"""fix-tritone-t-by-degree — secundário deceptivo (Chediak XXXIV(b)(1), p.114).

Um dominante-7 que atravessa a cascata aplicada sem casar nunca cai em `T` por
grau: em VI/III/bIII vira `Dsec` deceptivo com o alvo esperado `(V7/x)`."""

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis

H = HarmonicAnalysis("C", "major")


def _code(sym, nxt=None):
    return H.analyze_function(
        Chord(sym), None, Chord(nxt) if nxt else None, False, False
    )[0]


def test_vi7_deceptive_is_dsec_never_t():
    """A7 em Dó (VI7) sem resolução funcional: V7/II deceptivo (p.114)."""
    assert _code("A7", "C7M") == "Dsec"
    code, name, desc = H.analyze_function(Chord("A7"), None, Chord("C7M"), False, False)
    assert "V7/II" in name and "p.114" in desc


def test_iii7_deceptive_is_dsec_never_t():
    """E7 em Dó (III7) resolvendo fora do alvo: V7/VI deceptivo."""
    code, name, _ = H.analyze_function(Chord("E7"), None, Chord("G7"), False, False)
    # E7→G7 não é 4ªJ (seria A) nem ½t: cai no 0f
    assert code == "Dsec" and "V7/VI" in name


def test_biii7_deceptive_is_dsec():
    """Eb7 em Dó (bIII7) sem casar ramo: deceptivo, nunca T."""
    assert _code("Eb7", "C7M") == "Dsec"


def test_last_chord_vi7_is_deceptive_without_next():
    """Sem next_chord (fim da música), VI7 também é deceptivo (D3 do design)."""
    assert _code("A7") == "Dsec"


def test_genuine_secondary_still_detected():
    """A resolução funcional continua precedendo o 0f: A7→Dm7 = V7/II normal."""
    code, name, _ = H.analyze_function(Chord("A7"), None, Chord("Dm7"), False, False)
    assert code == "Dsec" and "deceptivo" not in name


def test_blues_i7_iv7_untouched():
    assert _code("C7", "F7") in ("T",)     # I7 blues (0a)
    assert _code("F7", "C7") in ("SD",)    # IV7 blues (0a)


def test_special_function_positions_have_their_own_reading():
    """II7 e VII7 não caem no 0f (VI/III/bIII): têm leitura própria de função
    especial (classify-special-function-dominants, Chediak p.112-113) — II7 é
    subdominante alterada, VII7 sem tônica é V7/III."""
    code, name, _ = H.analyze_function(Chord("D7"), None, Chord("C7M"), False, False)
    assert code == "SD" and "II7" in name
    code, name, _ = H.analyze_function(Chord("B7"), None, Chord("F7M"), False, False)
    assert code == "Dsec" and "V7/III" in name
