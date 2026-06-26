"""Validação: harness de acurácia da detecção de tonalidade."""

from harmonic_analysis.validation.key_accuracy import (
    KeyEval,
    evaluate_corpus,
    evaluate_song,
    is_relative,
    load_corpus,
    parse_key,
)

__all__ = [
    "KeyEval",
    "evaluate_corpus",
    "evaluate_song",
    "is_relative",
    "load_corpus",
    "parse_key",
]
