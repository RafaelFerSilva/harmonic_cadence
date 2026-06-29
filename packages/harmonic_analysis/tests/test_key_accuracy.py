"""Harness de acurácia de tonalidade."""

from harmonic_analysis.validation import (
    evaluate_corpus,
    evaluate_modulating_song,
    evaluate_song,
    is_relative,
    parse_key,
    same_collection,
)

# Progressões sintéticas claras (i-iv-V7-i / I-IV-V7-I em Ré).
DM = ["Dm", "Gm", "A7", "Dm"] * 3      # 12 acordes, Ré menor
DMAJ = ["D", "G", "A7", "D"] * 3       # 12 acordes, Ré maior


def test_parse_key():
    assert parse_key("G") == (7, "major")
    assert parse_key("Am") == (9, "minor")
    assert parse_key("F#m") == (6, "minor")
    assert parse_key("Bb") == (10, "major")
    assert parse_key("") is None
    assert parse_key("xyz") is None


def test_is_relative():
    assert is_relative((0, "major"), (9, "minor"))      # Dó maior / Lá menor
    assert is_relative((9, "minor"), (0, "major"))
    assert not is_relative((0, "major"), (7, "major"))
    assert not is_relative((0, "major"), (0, "minor"))  # paralela ≠ relativa


def test_same_collection_diatonic_degrees_of_major():
    C = (0, "major")
    assert same_collection(C, (4, "minor"))   # mediante iii (E), offset 4
    assert same_collection(C, (7, "major"))   # dominante V (G), offset 7
    assert same_collection(C, (9, "minor"))   # relativa vi (A), offset 9
    assert not same_collection((9, "major"), (0, "major"))  # A maior → C: offset 3


def test_same_collection_minor_gold():
    Am = (9, "minor")  # coleção {0,2,3,5,7,8,10} a partir de Lá
    assert same_collection(Am, (0, "major"))   # relativa maior (C), offset 3
    assert same_collection(Am, (4, "minor"))   # v menor (E), offset 7
    assert not same_collection(Am, (10, "major"))  # Bb: offset 1, cromático


def test_same_collection_ignores_detected_mode():
    # Mesmo offset diatônico conta independe do rótulo maior/menor detectado.
    C = (0, "major")
    assert same_collection(C, (4, "major")) and same_collection(C, (4, "minor"))


def test_evaluate_song_fills_same_collection():
    e = evaluate_song("c", ["C", "F", "G7", "C"], "C")
    assert e is not None and e.same_collection  # exato ⇒ coleção


def test_corpus_exposes_collection_accuracy():
    songs = [("c", ["C", "F", "G7", "C"], "C")]
    m = evaluate_corpus(songs)
    assert "collection_accuracy" in m
    assert 0.0 <= m["collection_accuracy"] <= 1.0


def test_metric_nesting_invariant():
    # exata ⊆ relativa-consciente ⊆ coleção, num corpus sintético misto.
    songs = [
        ("c", ["C", "F", "G7", "C"], "C"),      # exato
        ("g", ["G", "C", "D7", "G"], "G"),      # exato
        ("am", ["Am", "Dm", "E7", "Am"], "C"),  # gold C, detecta vizinhança
    ]
    m = evaluate_corpus(songs)
    assert m["exact_accuracy"] <= m["relative_aware_accuracy"]
    assert m["relative_aware_accuracy"] <= m["collection_accuracy"]


# NOTA: os testes do tier de centro ancorado no `cc_key` (`center_ok`, `verified`/`chediak`
# offsets, `center_accuracy`) foram REMOVIDOS — o Cifra Club foi aposentado como ouro. O
# centro tonal agora é validado pelo critério FUNCIONAL do Chediak no
# `scripts/songbook_baseline.py` (ver `test_functional_center.py`).


def test_evaluate_clear_major_is_exact():
    e = evaluate_song("c", ["C", "F", "G7", "C"], "C")
    assert e is not None
    assert e.detected[1] == "major"
    assert e.exact and e.mode_ok and not e.relative


def test_corpus_metrics_and_relative_aware_invariant():
    songs = [
        ("c", ["C", "F", "G7", "C"], "C"),
        ("g", ["G", "C", "D7", "G"], "G"),
    ]
    m = evaluate_corpus(songs)
    assert m["n"] == 2
    for k in ("mode_accuracy", "exact_accuracy", "relative_aware_accuracy"):
        assert 0.0 <= m[k] <= 1.0
    # relativa-consciente = exata ∪ relativa ⊇ exata
    assert m["relative_aware_accuracy"] >= m["exact_accuracy"]


def test_missing_annotation_is_excluded():
    assert evaluate_song("x", ["C", "F"], "") is None


# --- gold multi-região (músicas modulantes) --------------------------------


def test_modulating_song_partial_when_only_primary_present():
    ev = evaluate_modulating_song("dm-only", DM, "Dm", ["D"])
    assert ev is not None
    assert ev.primary_gold == (2, "minor")
    assert ev.secondary_golds == ((2, "major"),)
    assert ev.primary_ok            # Ré menor é a tônica detectada
    assert not ev.all_ok            # Ré maior nunca aparece → não é acerto total


def test_modulating_song_full_when_both_areas_present():
    ev = evaluate_modulating_song("dm-then-dmaj", DM + DMAJ, "Dm", ["D"])
    assert ev is not None
    assert (2, "minor") in ev.detected_regions
    assert (2, "major") in ev.detected_regions
    assert ev.all_ok and ev.primary_ok


def test_modulating_song_none_without_detection():
    assert evaluate_modulating_song("empty", [], "Dm", ["D"]) is None
