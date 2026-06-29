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


# --- dominante auxiliar (alvo de empréstimo modal) — Chediak XVIII-b, p.99 -----


def test_bvii7_resolving_a_fifth_below_is_auxiliary_dominant():
    # Bb7 → Eb (5ª abaixo, alvo bIII emprestado): dominante auxiliar, NÃO bVII7 Emp.
    code, name, _ = _fn("C", "Bb7", "Eb")
    assert code == "Daux"
    assert "V7/bIII" in name


def test_dominant_resolving_to_borrowed_bvi_is_auxiliary():
    code, name, _ = _fn("C", "Eb7", "Ab")
    assert code == "Daux"
    assert "V7/bVI" in name


def test_bvii7_not_resolving_a_fifth_below_stays_minor_subdominant():
    # Bb7 → C (sobe 1 tom): segue subdominante menor bVII7, não auxiliar.
    code, _, _ = _fn("C", "Bb7", "C")
    assert code == "Emp"


def test_blues_i7_and_iv7_are_not_auxiliary_dominants():
    assert _fn("C", "C7", "F")[0] == "T"   # I7 blues
    assert _fn("C", "F7", "Bb")[0] == "SD"  # IV7 blues


# --- SubV7 secundário (alvo diatônico) — Chediak XVIII-c, p.99 -----------------


def test_ab7_to_g_is_secondary_subv_of_v():
    code, name, _ = _fn("C", "Ab7", "G")
    assert code == "SubV"
    assert "SubV7/V" in name


def test_eb7_to_dm_is_secondary_subv_of_ii():
    code, name, _ = _fn("C", "Eb7", "Dm")
    assert code == "SubV"
    assert "SubV7/ii" in name


def test_primary_subv_to_tonic_is_unchanged():
    # Db7 → C continua o SubV primário (não recebe rótulo secundário).
    code, name, _ = _fn("C", "Db7", "C")
    assert code == "SubV"
    assert "secundário" not in name.lower()


def test_no_applied_dominant_is_labeled_v7_none():
    # Nenhum dos casos vira "V7/None" (o bug do alvo não-diatônico no Dsec antigo).
    cases = [("C", "Bb7", "Eb"), ("C", "Eb7", "Ab"), ("C", "Ab7", "G"), ("C", "Eb7", "Dm")]
    assert all("None" not in _fn(*c)[1] for c in cases)


# --- dominante estendido (resolve em outro dominante) — Chediak XXVIII(a), p.107 ---


def test_a7_to_d7_is_extended_dominant_not_secondary():
    # A7 resolve em D7 (outro dominante, 4ªJ acima) → pertence à cadeia, não ao tom.
    code, name, _ = _fn("C", "A7", "D7")
    assert code == "Dext"
    assert "Estendido" in name
    assert "V7/II" not in name


def test_extended_dominant_chain_last_link_reconnects():
    # A7 D7 G7 C: A7,D7 estendidos; G7 (alvo tônica) volta a ser dominante normal.
    assert _fn("C", "A7", "D7")[0] == "Dext"
    assert _fn("C", "D7", "G7")[0] == "Dext"
    assert _fn("C", "G7", "C")[0] == "D"


def test_bb7_to_eb7_is_extended_not_auxiliary():
    # Antes era Daux (alvo de empréstimo); resolvendo em Eb7 (dominante) é estendido.
    code, _, _ = _fn("C", "Bb7", "Eb7")
    assert code == "Dext"


def test_extended_dominant_takes_mixolydian_scale():
    from harmonic_analysis.domain import chord_scale

    h = HarmonicAnalysis("C", "major")
    # D7 (II7) sozinho cairia em lydian b7 (p.113); estendido força mixolídio (p.339).
    mode, _ = chord_scale.recommended_scale(Chord("D7"), h, Chord("G7"))
    assert mode == "mixolydian"


def test_extended_dominant_carries_no_applied_numeral():
    h = HarmonicAnalysis("C", "major")
    rn = h.roman_numeral(Chord("A7"), Chord("D7"))
    assert rn != "V7/II"
    assert rn == "A7"  # cifra analítica = o próprio acorde (sem grau)


def test_dominant_into_diatonic_target_stays_secondary():
    # Guard: alvo diatônico não-dominante (Am) segue Dsec, não Dext.
    code, name, _ = _fn("C", "E7", "Am")
    assert code == "Dsec"
    assert "V7/vi" in name


def test_blues_iv7_not_extended_even_before_fourth_above_dominant():
    # F7 (IV7 blues) seguido de Bb7 (4ªJ acima) continua SD blues, não Dext.
    code, _, _ = _fn("C", "F7", "Bb7")
    assert code == "SD"
