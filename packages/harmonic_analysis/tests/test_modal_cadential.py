"""Acordes cadenciais e evitados por modo (Chediak pp. 122-125)."""

import re

import pytest

from harmonic_analysis.domain.modal import (
    MODAL_AVOID,
    MODAL_CADENTIAL,
    modal_field,
)

_DEG = re.compile(r"^([#b]?(?:VII|VI|IV|V|III|II|I))")


def _degree(label):
    m = _DEG.match(label)
    return m.group(1) if m else None


def test_dorian():
    assert MODAL_CADENTIAL["dorian"] == ["IIm7", "IV7", "bVII7M"]
    assert MODAL_AVOID["dorian"] == ["VIm7(b5)"]


def test_mixolydian():
    assert MODAL_CADENTIAL["mixolydian"] == ["I7", "Vm7", "bVII7M"]
    assert MODAL_AVOID["mixolydian"] == ["IIIm7(b5)"]


def test_phrygian():
    assert MODAL_CADENTIAL["phrygian"] == ["bII7M", "bVIIm7"]
    assert MODAL_AVOID["phrygian"] == ["Vm7(b5)", "bIII7"]


def test_lydian_and_aeolian():
    assert MODAL_CADENTIAL["lydian"] == ["II7", "V7M", "VIIm7"]
    assert MODAL_AVOID["lydian"] == ["#IVm7(b5)"]
    assert MODAL_CADENTIAL["aeolian"] == ["IVm7", "bVI7M", "bVII7"]
    assert MODAL_AVOID["aeolian"] == ["IIm7(b5)"]


@pytest.mark.parametrize(
    "mode", ["dorian", "phrygian", "lydian", "mixolydian", "aeolian"]
)
def test_cadential_and_avoid_degrees_belong_to_the_field(mode):
    # integridade: todo cadencial/evitado é um grau do campo modal derivado
    field_degrees = {d for d, _q in modal_field("C", mode)}
    for label in MODAL_CADENTIAL[mode] + MODAL_AVOID[mode]:
        assert _degree(label) in field_degrees
