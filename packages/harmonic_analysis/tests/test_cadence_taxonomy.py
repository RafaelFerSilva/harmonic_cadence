"""Taxonomia de cadências do Chediak (pp. 109-111)."""

from harmonic_analysis.domain.cadence import analyze_cadences


def cad(degrees, chords):
    return analyze_cadences(degrees, "major", chords)


def test_perfect_cadence_root_position():
    c = cad(["V", "I"], ["G7", "C"])
    assert "G7 → C" in c["Perfeita"]
    assert c["Imperfeita"] == set()


def test_inverted_v_i_is_imperfect():
    c = cad(["V", "I"], ["G7", "C/E"])
    assert "G7 → C/E" in c["Imperfeita"]
    assert c["Perfeita"] == set()


def test_vii_i_is_imperfect():
    c = cad(["vii°", "I"], ["Bm7b5", "C"])
    assert "Bm7b5 → C" in c["Imperfeita"]


def test_plagal_includes_iv_i_and_ii_i():
    assert "F → C" in cad(["IV", "I"], ["F", "C"])["Plagal"]
    assert "Dm → C" in cad(["ii", "I"], ["Dm", "C"])["Plagal"]


def test_deceptive_is_v_to_any_non_tonic():
    assert "G7 → Am" in cad(["V", "vi"], ["G7", "Am"])["Deceptiva"]
    assert "G7 → F" in cad(["V", "IV"], ["G7", "F"])["Deceptiva"]


def test_half_cadence_rests_on_dominant():
    assert "Dm → G" in cad(["ii", "V"], ["Dm", "G"])["Meia-cadência"]


def test_authentic_is_prepared_perfect_cadence():
    c = cad(["ii", "V", "I"], ["Dm7", "G7", "C"])
    assert "Dm7 → G7 → C" in c["Autêntica"]
    assert "G7 → C" in c["Perfeita"]
