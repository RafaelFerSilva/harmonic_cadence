"""Corpus de validação de detecção de tonalidade + métrica de acurácia.

Progressões sintéticas com tonalidade conhecida (determinístico, offline).
Anotações de músicas reais podem ser acrescentadas com cifras em cache.
"""

from harmonic_analysis.domain.key_detection import detect_key

# (rótulo, acordes, tonalidade esperada)
CORPUS = [
    ("I-IV-V maior em C", ["C", "F", "G", "C", "Am", "Dm", "G", "C"], "C major"),
    ("I-IV-V maior em G", ["G", "C", "D", "G", "Em", "Am", "D", "G"], "G major"),
    ("I-IV-V maior em F", ["F", "Bb", "C", "F", "Dm", "Gm", "C", "F"], "F major"),
    ("I-IV-V maior em D", ["D", "G", "A", "D", "Bm", "Em", "A", "D"], "D major"),
    ("I-IV-V maior em Bb", ["Bb", "Eb", "F", "Bb", "Gm", "Cm", "F", "Bb"], "Bb major"),
    ("I-IV-V maior em A", ["A", "D", "E", "A", "F#m", "Bm", "E", "A"], "A major"),
    ("I-IV-V maior em Eb", ["Eb", "Ab", "Bb", "Eb", "Cm", "Fm", "Bb", "Eb"], "Eb major"),
    ("i-iv-V menor em Am", ["Am", "Dm", "E7", "Am", "F", "E7", "Am"], "A minor"),
    ("i-iv-V menor em Em", ["Em", "Am", "B7", "Em", "C", "B7", "Em"], "E minor"),
    ("i-iv-V menor em Dm", ["Dm", "Gm", "A7", "Dm", "Bb", "A7", "Dm"], "D minor"),
    ("ii-V-I jazz em C", ["Dm7", "G7", "Cmaj7", "Dm7", "G7", "Cmaj7"], "C major"),
    ("ii-V-I jazz em F", ["Gm7", "C7", "Fmaj7", "Gm7", "C7", "Fmaj7"], "F major"),
]


def test_key_detection_accuracy_meets_threshold():
    hits = 0
    misses = []
    for label, chords, expected in CORPUS:
        est = detect_key(chords)
        got = est.name if est else None
        if got == expected:
            hits += 1
        else:
            misses.append(f"{label}: esperado {expected}, obtido {got}")

    accuracy = hits / len(CORPUS)
    # Gate: pesos calibrados (root=2, cadência=2) atingem 100% neste corpus;
    # 0.90 deixa margem sem afrouxar a trava de regressão.
    assert accuracy >= 0.90, f"acurácia {accuracy:.0%}; erros: {misses}"
