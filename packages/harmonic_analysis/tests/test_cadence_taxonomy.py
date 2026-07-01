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


def test_deceptive_diatonic_is_v_to_any_non_tonic():
    # sem informação de região → diatônica (padrão)
    assert "G7 → Am" in cad(["V", "vi"], ["G7", "Am"])["Deceptiva diatônica"]
    assert "G7 → F" in cad(["V", "IV"], ["G7", "F"])["Deceptiva diatônica"]


def test_deceptive_modulating_across_a_key_change():
    # V em Dó seguido de acorde que inicia uma região tonal em Ré
    c = analyze_cadences(["V", "II"], "major", ["G7", "D"], chord_keys=["C", "D"])
    assert "G7 → D" in c["Deceptiva modulante"]
    # mesmo tom em ambos → diatônica
    c2 = analyze_cadences(["V", "vi"], "major", ["G7", "Am"], chord_keys=["C", "C"])
    assert "G7 → Am" in c2["Deceptiva diatônica"]


def test_half_cadence_rests_on_dominant():
    assert "Dm → G" in cad(["ii", "V"], ["Dm", "G"])["Meia-cadência"]


def test_authentic_is_prepared_perfect_cadence():
    c = cad(["ii", "V", "I"], ["Dm7", "G7", "C"])
    assert "Dm7 → G7 → C" in c["Autêntica"]
    assert "G7 → C" in c["Perfeita"]


# --- Coerência cadência×função (Chediak XXXII p.110: cadência = combinação D+T) ---


def test_v_i_with_dominant_function_target_is_not_a_cadence():
    # B7→Em7 é V→I por grau, mas Em7 FUNCIONA como D2 (ii cadencial) — resolução direta
    # (XXXIII), não cadência: suprimido, e NÃO reclassificado como deceptiva.
    c = analyze_cadences(
        ["V", "I"], "major", ["B7", "Em7"], function_codes=["D", "D2"]
    )
    assert c["Perfeita"] == set()
    assert c["Imperfeita"] == set()
    assert c["Autêntica"] == set()
    assert "B7 → Em7" not in c["Deceptiva diatônica"]
    assert "B7 → Em7" not in c["Deceptiva modulante"]


def test_v_i_with_diminished_function_target_is_not_a_cadence():
    c = analyze_cadences(
        ["V", "I"], "major", ["E7", "A°"], function_codes=["D", "Dim"]
    )
    assert c["Perfeita"] == set()
    assert c["Imperfeita"] == set()


def test_plagal_with_dominant_function_target_is_suppressed():
    c = analyze_cadences(
        ["II", "I"], "major", ["B7", "Am7"], function_codes=["Outro", "D2"]
    )
    assert c["Plagal"] == set()


def test_v_i_with_tonic_function_target_is_still_a_cadence():
    # Regressão: alvo de função T ⇒ cadência normal (a guarda só mira tensão).
    c = analyze_cadences(["V", "I"], "major", ["G7", "C"], function_codes=["D", "T"])
    assert "G7 → C" in c["Perfeita"]


def test_function_guard_is_opt_in_backward_compatible():
    # Sem function_codes ⇒ classificação grau-puro idêntica (compat).
    c = analyze_cadences(["V", "I"], "major", ["B7", "Em7"])
    assert "B7 → Em7" in c["Perfeita"]
