"""Caracterização da finalização da migração de spelling de nota (finish-note-spelling).

Estado-alvo: a descrição de empréstimo modal e o campo modal derivado grafam
bemóis corretamente (Bb, não A#); a detecção de origem funciona para acordes
bemóis; e os entry points standalone usam detect_key (K-S), não guess_key.
"""

from harmonic_analysis.domain.functional_hmm import parse_progression
from harmonic_analysis.domain.harmony import HarmonicAnalysis

SHARP_SPELLINGS = ("A#", "D#", "G#", "C#", "F#")


def test_harmonic_field_c_major_qualities_unchanged():
    """O campo maior de Dó (sem acidentes) permanece estruturalmente idêntico."""
    field = HarmonicAnalysis("C", "major")._build_harmonic_field("maior")
    assert field == (
        "I: Cmaj7 | ii: Dm7 | iii: Em7 | IV: Fmaj7 | V: G7 | vi: Am7 | vii°: Bm7b5"
    )


def test_harmonic_field_flat_key_spells_with_flats():
    """Em Fá maior, o campo da menor paralela grafa bemóis (Ab, Bb, Db, Eb)."""
    field = HarmonicAnalysis("F", "major")._build_harmonic_field("menor_natural")
    assert "Abmaj7" in field
    assert "Bbm7" in field
    assert "Dbmaj7" in field
    assert "Eb7" in field
    # E nunca o colapso sustenido-só legado.
    for sharp in ("A#", "G#", "C#", "D#"):
        assert sharp not in field


def test_borrowing_identifies_flat_origin():
    """describe_modal_borrowing acha a origem de um acorde bemol (antes: 'não
    identificada' por comparar string sustenido contra raiz bemol)."""
    desc = HarmonicAnalysis("F", "major").describe_modal_borrowing("Ab")
    assert desc != "Origem não identificada"
    assert "Ab" in desc
    for sharp in SHARP_SPELLINGS:
        assert sharp not in desc


def test_borrowing_preserves_multi_origin_structure():
    """A saída multi-origem (modos paralelos separados por '||') é preservada."""
    desc = HarmonicAnalysis("C", "major").describe_modal_borrowing("Eb")
    assert desc != "Origem não identificada"
    # Eb vem de mais de um modo paralelo de Dó (natural, harmônica, dórico...).
    assert "||" in desc


def test_standalone_parse_uses_detect_key_not_guess_key():
    """parse_progression(sem key) analisa contra o tom do detect_key (K-S).

    Em 'G7 C', guess_key diz 'G maior' (G7=tônica) e detect_key diz 'C maior'
    (G7=dominante). O parse deve seguir o K-S: G7→D, C→T.
    """
    path = parse_progression(["G7", "C"]).to_dict()["path"]
    assert path == ["D", "T"]


def test_guess_key_heuristic_is_retired():
    """A heurística fraca não sobrevive no código."""
    assert not hasattr(HarmonicAnalysis, "guess_key")
