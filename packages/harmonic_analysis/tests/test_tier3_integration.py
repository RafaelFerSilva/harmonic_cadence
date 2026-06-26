"""Camada 3 — integração: parsing probabilístico, reharmonização e explicação
populados pelo `AnalysisService` no caminho offline, sem regressão da Camada 2."""

from harmonic_analysis.services.analysis_service import AnalysisService


def _analyze(cifra_lines):
    return AnalysisService(None).analyze_song_data_structured(
        {"name": "x", "artist": "y", "cifra": cifra_lines}
    )


def test_tier3_sections_present():
    r = _analyze(["C F G7 C", "Am Dm7 G7 C"])
    assert r["success"] is True

    # functional_parse (HMM)
    fp = r["functional_parse"]
    assert fp is not None
    assert fp["path"][:4] == ["T", "SD", "D", "T"]
    assert all("confidence" in c for c in fp["chords"])

    # reharmonizations
    assert isinstance(r["reharmonizations"], list)
    assert any(s["technique"] == "tritone_substitution" for s in r["reharmonizations"])

    # explanation (template offline por padrão)
    assert isinstance(r["explanation"], str)
    assert "C maior" in r["explanation"]


def test_tier3_does_not_regress_tier2_sections():
    r = _analyze(["C  C/E  F  G7/B", "Am  Dm7  G7  Cmaj7"])
    # seções da Camada 1–2 continuam presentes
    for section in ("roman_numerals", "voice_leading", "chord_scales", "tonal_regions"):
        assert section in r
    assert "I6" in r["roman_numerals"]
    assert r["voice_leading"]["bass_line"][1] == "E"


def test_tier3_full_offline_path_is_deterministic():
    a = _analyze(["C F G7 C", "Am Dm7 G7 C"])
    b = _analyze(["C F G7 C", "Am Dm7 G7 C"])
    assert a["functional_parse"] == b["functional_parse"]
    assert a["reharmonizations"] == b["reharmonizations"]
    assert a["explanation"] == b["explanation"]
