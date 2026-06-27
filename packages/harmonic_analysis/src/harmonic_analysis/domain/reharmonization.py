"""Motor de reharmonização (Camada 3 — D2).

Biblioteca de transformações regradas e idiomáticas sobre uma progressão:
substituto de trítono, inserção de dominante secundário, interpolação de ii–V,
intercâmbio modal e substituição diatônica. Cada sugestão **preserva a função
harmônica** do ponto que altera e carrega técnica + justificativa. Determinístico
e offline; reusa as classes de altura/escala da Camada 1–2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from cifra_core.theory import root_pitch_class

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis
from harmonic_analysis.domain.key_detection import detect_key

# Nome preferido por classe de altura (bemóis — combina com bII7/SubV e empréstimos).
PC_TO_NAME = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Ordem de frequência idiomática (técnicas comuns primeiro) → desempata o ranking.
TECHNIQUE_RANK = {
    "tritone_substitution": 0,
    "secondary_dominant": 1,
    "ii_v_interpolation": 2,
    "diatonic_substitution": 3,
    "modal_interchange": 4,
}


@dataclass(frozen=True)
class Suggestion:
    """Uma sugestão de reharmonização, rotulada e justificada."""

    technique: str
    operation: str  # "replace" | "insert_before"
    positions: tuple  # índices afetados na progressão original
    original: tuple  # acordes originais no(s) ponto(s)
    result: tuple  # acordes de substituição/inserção
    function: str  # função preservada (macro: T/SD/D)
    rationale: str

    def to_dict(self) -> dict:
        return {
            "technique": self.technique,
            "operation": self.operation,
            "positions": list(self.positions),
            "original": list(self.original),
            "result": list(self.result),
            "function": self.function,
            "rationale": self.rationale,
        }


def _name(pc: int) -> str:
    return PC_TO_NAME[pc % 12]


def _is_dominant_resolving(chord: Chord, target: Chord) -> bool:
    """True se `chord` é dominante (com 7ª) e resolve uma 5ª justa abaixo de `target`."""
    if not chord.is_dominant_seventh:
        return False
    try:
        return (root_pitch_class(target.symbol) - root_pitch_class(chord.symbol)) % 12 == 5
    except Exception:
        return False


def _tritone_sub(i: int, chord: Chord, target: Chord) -> Optional[Suggestion]:
    """G7→C ⇒ Db7→C: troca o dominante pelo seu substituto de trítono (bII7)."""
    if not _is_dominant_resolving(chord, target):
        return None
    sub_pc = (root_pitch_class(chord.symbol) + 6) % 12
    sub = f"{_name(sub_pc)}7"
    return Suggestion(
        technique="tritone_substitution",
        operation="replace",
        positions=(i,),
        original=(chord.symbol,),
        result=(sub,),
        function="D",
        rationale=(
            f"{sub} é o substituto de trítono de {chord.symbol}: compartilham o "
            f"trítono das guide tones (3ª e 7ª) e resolvem em {target.symbol}, "
            "preservando a função dominante com baixo cromático descendente."
        ),
    )


def _secondary_dominant(
    i: int, chord: Chord, analysis: HarmonicAnalysis
) -> Optional[Suggestion]:
    """Insere o V7 do alvo diatônico antes dele (… → A7 Dm)."""
    degree = analysis.get_degree(chord)
    if degree is None or degree.upper() == "I":
        return None  # alvo precisa ser diatônico e não a própria tônica
    try:
        target_pc = root_pitch_class(chord.symbol)
    except Exception:
        return None
    dom_pc = (target_pc + 7) % 12  # 5ª justa acima
    dom = f"{_name(dom_pc)}7"
    return Suggestion(
        technique="secondary_dominant",
        operation="insert_before",
        positions=(i,),
        original=(chord.symbol,),
        result=(dom, chord.symbol),
        function="D",
        rationale=(
            f"{dom} é o V7/{degree} de {chord.symbol}: toniciza o alvo com seu "
            "próprio dominante (resolução de 5ª justa abaixo), sem mudar a função "
            "do acorde-alvo."
        ),
    )


def _ii_v_interpolation(
    i: int, chord: Chord, analysis: HarmonicAnalysis
) -> Optional[Suggestion]:
    """Interpola um ii–V do alvo antes dele (… → Dm7 G7 C)."""
    degree = analysis.get_degree(chord)
    if degree is None:
        return None
    try:
        target_pc = root_pitch_class(chord.symbol)
    except Exception:
        return None
    v_pc = (target_pc + 7) % 12
    ii_pc = (target_pc + 2) % 12
    ii = f"{_name(ii_pc)}m7"
    v = f"{_name(v_pc)}7"
    return Suggestion(
        technique="ii_v_interpolation",
        operation="insert_before",
        positions=(i,),
        original=(chord.symbol,),
        result=(ii, v, chord.symbol),
        function="D",
        rationale=(
            f"Interpola o ii–V de {chord.symbol} ({ii} {v}): prepara o alvo com a "
            "cadência ii–V mais idiomática do jazz/bossa, preservando seu papel."
        ),
    )


# Substituições diatônicas que preservam a função (relação de 3ª).
_DIATONIC_SUB = {
    "I": ("vi", "T"),
    "vi": ("I", "T"),
    "IV": ("ii", "SD"),
    "ii": ("IV", "SD"),
    "iii": ("I", "T"),
}


def _diatonic_sub(
    i: int, chord: Chord, analysis: HarmonicAnalysis
) -> Optional[Suggestion]:
    """Troca por um acorde diatônico de mesma função (I↔vi, IV↔ii)."""
    degree = analysis.get_degree(chord)
    if degree is None:
        return None
    entry = _DIATONIC_SUB.get(degree)
    if entry is None:
        return None
    sub_degree, function = entry
    sub = _chord_for_degree(sub_degree, analysis)
    if sub is None:
        return None
    return Suggestion(
        technique="diatonic_substitution",
        operation="replace",
        positions=(i,),
        original=(chord.symbol,),
        result=(sub,),
        function=function,
        rationale=(
            f"{sub} ({sub_degree}) substitui {chord.symbol} ({degree}): acordes "
            f"diatônicos a uma 3ª de distância compartilham a função {function}."
        ),
    )


def _modal_interchange(
    i: int, chord: Chord, analysis: HarmonicAnalysis
) -> Optional[Suggestion]:
    """Empréstimo do menor paralelo: IV→ivm (subdominante menor)."""
    degree = analysis.get_degree(chord)
    if degree != "IV" or chord.is_minor:
        return None
    sub = f"{chord.root}m"
    return Suggestion(
        technique="modal_interchange",
        operation="replace",
        positions=(i,),
        original=(chord.symbol,),
        result=(sub,),
        function="SD",
        rationale=(
            f"{sub} é o IV menor emprestado do modo menor paralelo: colore a "
            "subdominante com a 6ª menor (b13), mantendo a função subdominante."
        ),
    )


def _chord_for_degree(degree: str, analysis: HarmonicAnalysis) -> Optional[str]:
    """Acorde diatônico de um grau na tonalidade (com qualidade maior/menor)."""
    roman = degree.upper().lstrip("#b")
    table = ["I", "II", "III", "IV", "V", "VI", "VII"]
    if roman not in table:
        return None
    idx = table.index(roman)
    if idx >= len(analysis.scale_pcs):
        return None
    pc = analysis.scale_pcs[idx]
    name = _name(pc)
    return f"{name}m" if degree[:1].islower() else name


def reharmonize(
    chords: Sequence[Chord], analysis: HarmonicAnalysis
) -> List[Suggestion]:
    """Gera sugestões de reharmonização idiomáticas para a progressão.

    Cada sugestão é rotulada, justificada e preserva a função. O resultado é
    deduplicado e ordenado por frequência idiomática da técnica.
    """
    suggestions: List[Suggestion] = []
    n = len(chords)
    for i, chord in enumerate(chords):
        nxt = chords[i + 1] if i + 1 < n else None

        if nxt is not None:
            s = _tritone_sub(i, chord, nxt)
            if s:
                suggestions.append(s)

        # Inserções/substituições que dependem de um acorde precedente (i ≥ 1).
        if i >= 1:
            for builder in (
                _secondary_dominant,
                _ii_v_interpolation,
                _diatonic_sub,
                _modal_interchange,
            ):
                s = builder(i, chord, analysis)
                if s:
                    suggestions.append(s)

    return _rank_and_dedupe(suggestions)


def reharmonize_symbols(
    symbols: Sequence[str], key: Optional[str] = None, mode: str = "major"
) -> List[Suggestion]:
    """Reharmoniza a partir de símbolos (offline, sem provider) — útil em testes/CLI."""
    chords = [Chord(s) for s in symbols]
    if key is None:
        est = detect_key([c.symbol for c in chords])
        if est:
            key, mode = est.key_note, est.mode
    analysis = HarmonicAnalysis(key, mode)
    return reharmonize(chords, analysis)


def _rank_and_dedupe(suggestions: List[Suggestion]) -> List[Suggestion]:
    seen = set()
    unique: List[Suggestion] = []
    for s in suggestions:
        sig = (s.technique, s.positions, s.result)
        if sig in seen:
            continue
        seen.add(sig)
        unique.append(s)
    unique.sort(
        key=lambda s: (TECHNIQUE_RANK.get(s.technique, 99), s.positions)
    )
    return unique
