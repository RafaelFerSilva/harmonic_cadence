from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis


def _fn(key, sym, nxt):
    h = HarmonicAnalysis(key, "major")
    return h.analyze_function(Chord(sym), None, Chord(nxt) if nxt else None)


def test_e7_to_am_is_secondary_dominant_of_vi():
    code, name, _ = _fn("C", "E7", "Am")
    assert code == "Dsec"
    assert "V7/vi" in name


def test_d7_to_g_is_secondary_dominant_of_v():
    code, name, _ = _fn("C", "D7", "G")
    assert code == "Dsec"
    assert "V7/V" in name


def test_db7_to_c_is_subv():
    code, _, _ = _fn("C", "Db7", "C")
    assert code == "SubV"


def test_primary_dominant_g7_to_c_is_function_d_not_secondary():
    code, _, _ = _fn("C", "G7", "C")
    assert code == "D"


def test_inverted_fifth_relation_is_not_secondary_dominant():
    # alvo uma 5ª ACIMA da fundamental (relação invertida) não é Dsec por isso
    code, name, _ = _fn("C", "C7", "G")
    assert not (code == "Dsec" and "V7/V" in name)
