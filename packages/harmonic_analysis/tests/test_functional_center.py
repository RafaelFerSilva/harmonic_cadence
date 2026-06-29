"""Centro tonal pelo critério FUNCIONAL do Chediak (change `songbook-chediak-baseline`).

A tônica é ACHADA da música (dominante funcional resolvendo no repouso, pp.84/87), sem
`cc_key`. Invariante a transposição; conservador (quarentena quando não confirma).
"""

from harmonic_analysis.validation import chediak_functional_center as cfc

_PC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def test_finds_tonic_in_major_ii_V_I():
    assert cfc(["Dm7", "G7", "C7M"]) == (0, "major")  # G7→C


def test_finds_tonic_in_minor_ii_V_i():
    assert cfc(["Bm7(b5)", "E7", "Am7"]) == (9, "minor")  # E7→Am


def test_subv_resolution_counts():
    assert cfc(["Dm7", "Db7", "C7M"]) == (0, "major")  # SubV7 (Db7) → C


def test_secondary_dominant_does_not_become_tonic():
    # C7 = V7/IV resolve em F, mas F NÃO é a tônica: o repouso é C (primeiro acorde).
    assert cfc(["C7M", "C7", "F7M", "Dm7", "G7", "C7M"]) == (0, "major")


def test_static_modal_vamp_is_quarantined():
    # Sem dominante funcional resolvendo no repouso → None (quarentena).
    assert cfc(["Dm7", "G7", "Dm7", "G7"]) is None


def test_invariant_to_transposition():
    base = ["Dm7", "G7", "C7M"]
    for t in range(12):
        shifted = [_shift(c, t) for c in base]
        r = cfc(shifted)
        assert r is not None
        assert r[0] == (0 + t) % 12 and r[1] == "major"


def _shift(symbol: str, t: int) -> str:
    """Transpõe um símbolo simples (raiz + sufixo) por t semitons, p/ o teste."""
    import re

    m = re.match(r"^([A-G][#b]?)(.*)$", symbol)
    assert m
    from cifra_core.theory import Note

    pc = (Note.parse(m.group(1)).pitch_class + t) % 12
    return _PC[pc] + m.group(2)
