"""Condução de vozes: linha de baixo, pedais, baixo descendente, line clichés."""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from cifra_core.theory import Note

from harmonic_analysis.domain.chord import Chord


def bass_note(chord: Chord) -> str:
    """Baixo do acorde: o slash quando presente, senão a fundamental."""
    return chord.properties.bass or chord.root


def _bass_pc(chord: Chord) -> Optional[int]:
    try:
        return Note.parse(bass_note(chord)).pitch_class
    except Exception:
        return None


def bass_line(chords: Sequence[Chord]) -> List[Optional[int]]:
    return [_bass_pc(c) for c in chords]


def bass_motions(chords: Sequence[Chord]) -> List[Optional[int]]:
    """Movimento do baixo em semitons (com sinal, −6..+6) entre acordes sucessivos."""
    pcs = bass_line(chords)
    motions: List[Optional[int]] = []
    for a, b in zip(pcs, pcs[1:]):
        if a is None or b is None:
            motions.append(None)
            continue
        up = (b - a) % 12
        motions.append(up if up <= 6 else up - 12)
    return motions


def descending_runs(chords: Sequence[Chord], min_len: int = 3) -> List[Dict]:
    """Trechos de baixo descendente; distingue cromático de diatônico."""
    motions = bass_motions(chords)
    runs: List[Dict] = []
    i, n = 0, len(motions)
    while i < n:
        if motions[i] is not None and motions[i] < 0:
            j = i
            while j < n and motions[j] is not None and motions[j] < 0:
                j += 1
            if (j - i + 1) >= min_len:
                seg = motions[i:j]
                runs.append(
                    {
                        "start": i,
                        "end": j,
                        "chromatic": all(m == -1 for m in seg),
                    }
                )
            i = j
        else:
            i += 1
    return runs


def pedal_points(chords: Sequence[Chord], min_len: int = 3) -> List[Dict]:
    """Pedais: baixo sustentado sob acordes que mudam."""
    pcs = bass_line(chords)
    runs: List[Dict] = []
    i, n = 0, len(pcs)
    while i < n:
        j = i
        while j + 1 < n and pcs[j + 1] == pcs[i] and pcs[i] is not None:
            j += 1
        if (j - i + 1) >= min_len:
            symbols = {chords[k].symbol for k in range(i, j + 1)}
            if len(symbols) > 1:  # os acordes realmente mudam sobre o pedal
                runs.append({"start": i, "end": j, "bass": bass_note(chords[i])})
        i = j + 1
    return runs


def line_cliches(chords: Sequence[Chord], min_len: int = 3) -> List[Dict]:
    """Line clichés: mesma fundamental com a qualidade mudando cromaticamente."""
    runs: List[Dict] = []
    i, n = 0, len(chords)
    while i < n:
        j = i
        while j + 1 < n and chords[j + 1].root == chords[i].root:
            j += 1
        if (j - i + 1) >= min_len:
            symbols = {chords[k].symbol for k in range(i, j + 1)}
            if len(symbols) > 1:
                runs.append({"start": i, "end": j, "root": chords[i].root})
        i = j + 1
    return runs


def analyze(chords: Sequence[Chord]) -> Dict:
    """Resumo de condução de vozes para o relatório."""
    return {
        "bass_line": [bass_note(c) for c in chords],
        "descending": descending_runs(chords),
        "pedals": pedal_points(chords),
        "line_cliches": line_cliches(chords),
    }
