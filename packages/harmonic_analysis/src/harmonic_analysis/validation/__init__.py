"""Validação: harness de acurácia da detecção de tonalidade."""

from harmonic_analysis.validation.key_accuracy import (
    KeyEval,
    ModalCenterLedgerRow,
    MultiKeyEval,
    center_ok,
    evaluate_corpus,
    evaluate_modulating_song,
    evaluate_song,
    is_relative,
    load_corpus,
    modal_center_ledger,
    parse_key,
    same_collection,
)

__all__ = [
    "KeyEval",
    "ModalCenterLedgerRow",
    "MultiKeyEval",
    "center_ok",
    "evaluate_corpus",
    "evaluate_modulating_song",
    "evaluate_song",
    "is_relative",
    "load_corpus",
    "modal_center_ledger",
    "parse_key",
    "same_collection",
]
