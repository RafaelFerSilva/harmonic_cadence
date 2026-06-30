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


def test_dominant_target_does_not_establish_tonic():
    # A7(b9)→D7(13): o alvo D7 é DOMINANTE (trítono) — elo de cadeia V/V→V, não tônica.
    # Sem repouso num extremo, retorna None (quarentena honesta). (harden-functional-center)
    assert cfc(["Dm7(9)", "G7(13)", "A7(b9)", "D7(13)", "A7M"]) is None


def test_inverted_target_does_not_establish_tonic():
    # G7(#5)→Fm/C: o alvo é Fá menor invertido (raiz F ≠ baixo C) — é o iv, não a tônica.
    # Não pode virar "C minor"; o centro real (C major) vem de G7(9)→C (repouso, raiz==baixo).
    seq = ["G7(#5)", "Fm/C", "C7M", "Dm7", "G7(9)", "C"]
    r = cfc(seq)
    assert r != (0, "minor")  # nunca cunha Dó menor de um Fá menor
    assert r == (0, "major")  # acha o repouso real em C


def test_minor_repose_target_still_works():
    # V→i menor legítimo: D7(9)→Gm7 (alvo de repouso menor, raiz==baixo) → G minor.
    assert cfc(["Cm7", "D7(9)", "Gm7"]) == (7, "minor")


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
