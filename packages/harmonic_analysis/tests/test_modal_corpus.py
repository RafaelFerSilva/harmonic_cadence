"""Corpus de validação da detecção de modo (determinístico, offline)."""

from harmonic_analysis.domain.modal import detect_mode

# (rótulo, acordes resolvendo no "final", modo esperado | None se tonal)
CORPUS = [
    ("G mixolídio", ["G", "F", "C", "G"], "mixolydian"),
    ("A mixolídio", ["A", "G", "D", "A"], "mixolydian"),
    ("D mixolídio (baião)", ["D", "C", "G", "D"], "mixolydian"),
    ("D dórico", ["Dm", "G", "Em", "Dm"], "dorian"),
    ("A dórico", ["Am", "D", "Em", "Am"], "dorian"),
    ("E frígio", ["Em", "F", "Em"], "phrygian"),
    ("tonal maior (não modal)", ["C", "F", "G7", "C"], None),
    ("tonal menor (não modal)", ["Am", "Dm", "E7", "Am"], None),
]


def test_modal_detection_accuracy():
    hits = 0
    misses = []
    for label, chords, expected in CORPUS:
        info = detect_mode(chords)
        got = info.mode if info else None
        if got == expected:
            hits += 1
        else:
            misses.append(f"{label}: esperado {expected}, obtido {got}")
    accuracy = hits / len(CORPUS)
    assert accuracy >= 0.85, f"acurácia {accuracy:.0%}; erros: {misses}"
