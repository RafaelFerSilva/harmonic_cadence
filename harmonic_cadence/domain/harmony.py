from collections import Counter
from typing import List, Literal, Optional, Tuple

from harmonic_cadence.domain.chord import Chord
from harmonic_cadence.domain.constants import (
    CHROMATIC_NOTES,
    DEGREES_MAJOR,
    DEGREES_MINOR,
    HARMONIC_FUNCTIONS,
    MAJOR_SCALE,
    MINOR_SCALE,
    MODE_HARMONY,
    MODE_NAMES_PT,
    MODES,
    NOTE_REPLACEMENTS,
)

FunctionCode = Literal[
    "T", "SD", "D", "D2", "SubV", "Sub2", "Dsec", "Emp", "Dim", "Crom", "Outro"
]


class HarmonicAnalysis:
    """
    Realiza análise harmônica completa de uma progressão de acordes.
    """

    def __init__(self, key: str, mode: str = "major"):
        if not key or key[0] not in CHROMATIC_NOTES:
            raise ValueError(f"Tonalidade inválida: {key}")
        if mode not in ["major", "minor"]:
            raise ValueError(f"Modo inválido: {mode}")

        self.key = key
        self.mode = mode
        self.scale, self.degrees = self._build_scale()
        self.HARMONIC_FUNCTIONS = HARMONIC_FUNCTIONS

    def _build_scale(self) -> Tuple[List[str], List[str]]:
        """Constrói a escala e seus graus baseado na tonalidade e modo."""
        if self.mode == "major":
            idx = MAJOR_SCALE.index(self.key[0])
            scale = MAJOR_SCALE[idx:] + MAJOR_SCALE[:idx]
            degrees = DEGREES_MAJOR
        else:
            idx = MINOR_SCALE.index(self.key[0])
            scale = MINOR_SCALE[idx:] + MINOR_SCALE[:idx]
            degrees = DEGREES_MINOR

        if len(self.key) > 1:  # Considera alterações (#/b)
            scale[0] = self.key
        return scale, degrees

    def get_degree(self, chord: Chord) -> Optional[str]:
        """Determina o grau do acorde na tonalidade."""
        if chord.root in self.scale:
            degree = self.degrees[self.scale.index(chord.root)]
            if chord.is_minor and degree.isupper():
                return degree.lower()
            if not chord.is_minor and degree.islower():
                return degree.upper()
            return degree
        return None

    def analyze_function(
        self,
        chord: Chord,
        prev_chord: Optional[Chord] = None,
        next_chord: Optional[Chord] = None,
    ) -> Tuple[FunctionCode, str, str]:
        """
        Analisa a função harmônica do acorde no contexto.
        Retorna: (código_função, nome_função, descrição)
        """
        degree = self.get_degree(chord)

        # 1. Função clássica diatônica
        for func_code, func_info in self.HARMONIC_FUNCTIONS.items():
            if degree in func_info["degrees"]:
                return (func_code, func_info["name"], func_info["description"])

        # 2. Segunda Cadencial (II-V-I)
        if (
            degree in self.HARMONIC_FUNCTIONS["D2"]["degrees"]
            and next_chord
            and self.get_degree(next_chord) in ["V", "V7"]
        ):
            return (
                "D2",
                self.HARMONIC_FUNCTIONS["D2"]["name"],
                self.HARMONIC_FUNCTIONS["D2"]["description"],
            )

        # 3. Dominante Secundário
        if chord.is_dominant_seventh and next_chord:
            target_chord = next_chord
            target_root = target_chord.root
            if target_root and self._get_interval(chord.root, target_root) == 7:
                target_degree = self.get_degree(target_chord)
                return (
                    "Dsec",
                    f"Dominante Secundário (V7/{target_degree})",
                    self.HARMONIC_FUNCTIONS["Dsec"]["description"],
                )

        # 4. Substituto de Dominante (SubV7)
        if chord.is_dominant_seventh and self._get_interval(chord.root, self.key) == 1:
            return (
                "SubV",
                self.HARMONIC_FUNCTIONS["SubV"]["name"],
                self.HARMONIC_FUNCTIONS["SubV"]["description"],
            )

        # 5. Empréstimo Modal
        if degree is None:
            modal_source = self.describe_modal_borrowing(chord.root)
            return ("Emp", self.HARMONIC_FUNCTIONS["Emp"]["name"], modal_source)

        # 6. Aproximação Cromática
        if (
            prev_chord
            and next_chord
            and self._is_chromatic_approach(prev_chord, chord, next_chord)
        ):
            return (
                "Crom",
                self.HARMONIC_FUNCTIONS["Crom"]["name"],
                self.HARMONIC_FUNCTIONS["Crom"]["description"],
            )

        return (
            "Outro",
            "Função não identificada",
            "Acorde com função harmônica não classificada",
        )

    def describe_modal_borrowing(self, chord_root: str) -> str:
        """Identifica possíveis origens modais do acorde."""
        if chord_root == self.key:
            return "-"

        possible_sources = []
        for mode_name, scale in MODES.items():
            transposed_scale = self._transpose_scale(scale, self.key)
            if chord_root in transposed_scale:
                possible_sources.append(mode_name)

        if not possible_sources:
            return "Origem não identificada"

        descriptions = []
        for mode_name in possible_sources:
            nome = MODE_NAMES_PT.get(mode_name, mode_name)
            escala = " ".join(self._transpose_scale(MODES[mode_name], self.key))
            campo = self._build_harmonic_field(mode_name)
            descriptions.append(
                f"{nome} de {self.key}: [{escala}] | Campo harmônico: {campo}"
            )

        return " || ".join(descriptions)

    def _build_harmonic_field(self, mode_name: str) -> str:
        """Constrói o campo harmônico de um modo."""
        scale = MODES[mode_name]
        harmony = MODE_HARMONY.get(mode_name, [])
        transposed_scale = self._transpose_scale(scale, self.key)
        degrees = DEGREES_MAJOR if mode_name == "maior" else DEGREES_MINOR

        if len(transposed_scale) < 7:
            transposed_scale += [""] * (7 - len(transposed_scale))
        if len(harmony) < 7:
            harmony += [""] * (7 - len(harmony))
        if len(degrees) < 7:
            degrees += [""] * (7 - len(degrees))

        field = []
        for deg, note, chord_type in zip(degrees, transposed_scale, harmony):
            if note:
                field.append(f"{deg}: {note}{chord_type}")
        return " | ".join(field)

    @staticmethod
    def _normalize_note(note: str) -> str:
        """Normaliza uma nota para sua forma padrão."""
        return NOTE_REPLACEMENTS.get(note, note)

    @staticmethod
    def _get_interval(note1: str, note2: str) -> int:
        """Calcula o intervalo entre duas notas em semitons."""
        n1 = CHROMATIC_NOTES.index(HarmonicAnalysis._normalize_note(note1))
        n2 = CHROMATIC_NOTES.index(HarmonicAnalysis._normalize_note(note2))
        return (n2 - n1) % 12

    def _transpose_scale(self, scale: List[str], target_key: str) -> List[str]:
        """Transpõe uma escala para uma nova tonalidade."""
        base_note = "C"
        interval = self._get_interval(base_note, target_key)
        return [self._transpose_note(note, interval) for note in scale]

    def _transpose_note(self, note: str, interval: int) -> str:
        """Transpõe uma nota por um determinado intervalo."""
        n = CHROMATIC_NOTES.index(self._normalize_note(note))
        return CHROMATIC_NOTES[(n + interval) % 12]

    @staticmethod
    def _is_chromatic_approach(
        prev_chord: Chord, chord: Chord, next_chord: Chord
    ) -> bool:
        """Verifica se um acorde é uma aproximação cromática."""
        if not all([prev_chord.root, chord.root, next_chord.root]):
            return False
        interval = abs(HarmonicAnalysis._get_interval(chord.root, next_chord.root))
        return interval == 1

    @staticmethod
    def guess_key(chords: List[Chord]) -> Tuple[Optional[str], Optional[str]]:
        """Tenta adivinhar a tonalidade baseado nos acordes."""
        if not chords:
            return None, None

        first_chord = chords[0]

        # Usar Counter em vez de dicionário fixo
        qualities_counter = Counter(chord.quality for chord in chords)
        roots_counter = Counter(chord.root for chord in chords)

        total_chords = len(chords)
        # Usar .get() para evitar KeyError
        minor_ratio = (
            qualities_counter.get("minor", 0) / total_chords if total_chords > 0 else 0
        )

        if first_chord.is_minor or minor_ratio > 0.3:
            most_common_root = roots_counter.most_common(1)[0][0]
            return most_common_root, "minor"
        return first_chord.root, "major"
