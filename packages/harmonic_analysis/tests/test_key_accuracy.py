"""Harness de acurácia de tonalidade."""

from harmonic_analysis.validation import (
    evaluate_corpus,
    evaluate_song,
    is_relative,
    parse_key,
)


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
