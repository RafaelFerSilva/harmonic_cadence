"""dim7 como V7(b9) sem fundamental (rootless) — Chediak.

B°7 (B-D-F-Ab) = G7(b9) (G-B-D-F-Ab) sem o G → dominante de C. A fundamental
implícita está uma 3ª maior abaixo da raiz escrita; a tônica de resolução, um
semitom acima. Só é dominante quando resolve um semitom acima; senão é diminuto
de aproximação. A identidade sonora (Category.DIMINISHED, numeral °7) é preservada.
"""

from cifra_core.theory import realize

from harmonic_analysis.domain import chord_scale
from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis


def _fn(key, sym, nxt):
    h = HarmonicAnalysis(key, "major")
    return h.analyze_function(Chord(sym), None, Chord(nxt) if nxt else None)


# --- função: dim7-dominante (resolve um semitom acima) ------------------------


def test_vii_dim7_to_tonic_is_primary_dominant():
    # B°7 → C: vii°7 = V7(b9) de I (alvo = tônica) → função D primária.
    code, name, _ = _fn("C", "B°7", "C")
    assert code == "D"
    assert "V7(b9)" in name


def test_ascending_sharp_i_dim7_is_secondary_dominant_of_ii():
    # C#°7 → Dm: dominante rootless de ii (A7(b9) sem A) → Dsec V7(b9)/ii.
    code, name, _ = _fn("C", "C#°7", "Dm")
    assert code == "Dsec"
    assert "V7(b9)/ii" in name


def test_sharp_iv_dim7_is_secondary_dominant_of_v():
    # F#°7 → G: dominante rootless de V (D7(b9) sem D) → Dsec V7(b9)/V.
    code, name, _ = _fn("C", "F#°7", "G")
    assert code == "Dsec"
    assert "V7(b9)/V" in name


def test_dim7_alias_spelling_is_recognized():
    # `Bdim7` é o mesmo que `B°7`.
    code, name, _ = _fn("C", "Bdim7", "C")
    assert code == "D"
    assert "V7(b9)" in name


# --- gate: diminuto de aproximação/passagem NÃO é dominante -------------------


def test_dim7_not_resolving_semitone_up_is_not_dominant():
    # B°7 → Am: o alvo NÃO está um semitom acima da raiz escrita → não é dominante.
    code, _, _ = _fn("C", "B°7", "Am")
    assert code not in ("D", "Dsec")


def test_dim7_without_next_chord_is_not_dominant():
    code, _, _ = _fn("C", "B°7", None)
    assert code not in ("D", "Dsec")


# --- identidade preservada (a tese é sobre função, não sobre o som) -----------


def test_diminished_identity_is_preserved():
    c = Chord("B°7")
    assert c.quality == "diminished"
    assert c.is_dominant_seventh is False


# --- escala-acorde diminuta (octatônica do dominante implícito) ---------------


def test_chromatic_dim7_keeps_altered_numeral_with_diminished_mark():
    h = HarmonicAnalysis("C", "major")
    assert h.roman_numeral(Chord("B°7"), Chord("C")) == "vii°7"   # diatônico
    assert h.roman_numeral(Chord("C#°7"), Chord("Dm")) == "#i°7"  # cromático
    assert h.roman_numeral(Chord("F#°7"), Chord("G")) == "#iv°7"


def test_dim7_maps_to_diminished_octatonic_scale():
    h = HarmonicAnalysis("C", "major")
    mode, notes = chord_scale.recommended_scale(Chord("B°7"), h)
    assert mode == "diminished"
    scale_pcs = {n.pitch_class for n in notes}
    # a coleção contém as notas do acorde…
    assert set(realize("B°7")) <= scale_pcs
    # …e é exatamente a octatônica do G7(b9) implícito (3ª maior abaixo).
    _, g_notes = chord_scale.recommended_scale(Chord("G7(b9)"), h)
    assert scale_pcs == {n.pitch_class for n in g_notes}
