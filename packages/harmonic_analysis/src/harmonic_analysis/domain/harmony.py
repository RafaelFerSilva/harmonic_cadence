from collections import Counter, defaultdict
from typing import Dict, List, Literal, Optional, Tuple

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.constants import (
    CHROMATIC_NOTES,
    DEGREES_MAJOR,
    DEGREES_MINOR,
    FUNCTION_PROGRESSIONS,
    HARMONIC_FUNCTIONS,
    MAJOR_SCALE,
    MINOR_SCALE,
    MODE_HARMONY,
    MODE_NAMES_PT,
    MODES,
    NOTE_REPLACEMENTS,
    PROGRESSION_CATEGORIES,
    PROGRESSIONS,
)

FunctionCode = Literal[
    "T", "SD", "D", "D2", "SubV", "Sub2", "Dsec", "Emp", "Dim", "Crom", "Outro"
]

VALID_NOTES = set(CHROMATIC_NOTES)


class HarmonicAnalysis:
    """
    Realiza análise harmônica completa de uma progressão de acordes.
    """

    def __init__(self, key: str, mode: str = "major"):
        if not key or key[0] not in CHROMATIC_NOTES:
            raise ValueError(f"Tonalidade inválida: {key}")

        self.key = key
        self.mode = mode
        self.scale, self.degrees = self._build_scale()
        self.HARMONIC_FUNCTIONS = HARMONIC_FUNCTIONS
        self.VALID_NOTES = VALID_NOTES

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
        try:
            normalized_root = self.normalize_note(chord.root)
        except ValueError:
            return None
        if normalized_root in self.scale:
            degree = self.degrees[self.scale.index(normalized_root)]
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

        # Validação do acorde
        if not self.validate_chord(chord):
            return (
                "Outro",
                "Acorde inválido",
                f"Acorde '{chord.symbol}' possui nota raiz inválida ou formato incorreto.",
            )
        degree = self.get_degree(chord)

        # 1. Função clássica diatônica (T, SD, D, Sub2, Dim, etc)
        for func_code, func_info in self.HARMONIC_FUNCTIONS.items():
            if degree in func_info["degrees"]:
                # Validações específicas para algumas funções
                if func_code == "Sub2":
                    # Exemplo: Substituto do IIm7 pode precisar de contexto (ex: próximo acorde)
                    if next_chord and self.get_degree(next_chord) in ["V", "V7"]:
                        return (func_code, func_info["name"], func_info["description"])
                    else:
                        continue  # Não é substituto se não preparar dominante

                if func_code == "Dim":
                    # Diminuto de passagem geralmente aparece entre acordes vizinhos
                    if prev_chord and next_chord:
                        interval_prev = self._get_interval(prev_chord.root, chord.root)
                        interval_next = self._get_interval(chord.root, next_chord.root)
                        # Exemplo: diminuto de passagem é meio tom entre acordes vizinhos
                        if interval_prev == 1 and interval_next == 1:
                            return (
                                func_code,
                                func_info["name"],
                                func_info["description"],
                            )
                        else:
                            continue  # Não é diminuto de passagem se não estiver entre vizinhos

                # Para outras funções, retorna direto
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

        # 7. Caso não identificado
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
    def normalize_note(note: str) -> str:
        if not note:
            raise ValueError("Nota vazia ou None não é válida")
        note = note.strip().capitalize()
        note = NOTE_REPLACEMENTS.get(note, note)
        if note not in CHROMATIC_NOTES:
            raise ValueError(f"Nota inválida após normalização: {note}")
        return note

    def validate_chord(self, chord: Chord) -> bool:
        try:
            normalized_root = self.normalize_note(chord.root)
        except Exception:
            return False
        return normalized_root in self.VALID_NOTES

    @staticmethod
    def _get_interval(note1: str, note2: str) -> int:
        """Calcula o intervalo entre duas notas em semitons."""
        n1 = CHROMATIC_NOTES.index(HarmonicAnalysis.normalize_note(note1))
        n2 = CHROMATIC_NOTES.index(HarmonicAnalysis.normalize_note(note2))
        return (n2 - n1) % 12

    def _transpose_scale(self, scale: List[str], target_key: str) -> List[str]:
        """Transpõe uma escala para uma nova tonalidade."""
        base_note = "C"
        interval = self._get_interval(base_note, target_key)
        return [self._transpose_note(note, interval) for note in scale]

    def _transpose_note(self, note: str, interval: int) -> str:
        """Transpõe uma nota por um determinado intervalo."""
        n = CHROMATIC_NOTES.index(self.normalize_note(note))
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

    @staticmethod
    def extract_sequences(harmonic_analysis):
        degrees = []
        functions = []
        for entry in harmonic_analysis:
            degree = entry.get("degree", None)
            function_code = entry.get("function_code", None)

            # Ignorar graus nulos (ex: acordes empréstimos modais)
            if degree:
                degrees.append(degree)
            else:
                degrees.append("X")  # Marcar como "desconhecido"

            functions.append(function_code)

        return degrees, functions

    from collections import Counter

    @staticmethod
    def analyze_function_stats(harmonic_analysis: List[dict]) -> List[Dict]:
        """Analisa estatísticas das funções harmônicas incluindo exemplos de acordes"""

        # 1. Contagem de funções com exemplos de acordes
        function_examples = defaultdict(list)
        for entry in harmonic_analysis:
            func = entry["function_code"]
            function_examples[func].append(entry["chord"])

        function_counts = {
            func: {
                "count": len(chords),
                "example_chords": list(set(chords))[:3],  # Mostra até 3 exemplos únicos
            }
            for func, chords in function_examples.items()
        }

        # 2. Transições com exemplos
        transition_examples = defaultdict(list)
        for i in range(len(harmonic_analysis) - 1):
            current = harmonic_analysis[i]
            next_chord = harmonic_analysis[i + 1]
            transition = (current["function_code"], next_chord["function_code"])
            transition_examples[transition].append(
                f"{current['chord']}→{next_chord['chord']}"
            )

        common_transitions = {
            f"{k[0]}→{k[1]}": {
                "count": len(examples),
                "example_progressions": list(set(examples))[
                    :3
                ],  # Até 3 exemplos únicos
            }
            for k, examples in transition_examples.items()
        }

        return [
            {
                "function_counts": function_counts,
                "common_transitions": common_transitions,
            }
        ]

    @staticmethod
    def detect_progressions(
        target_sequences, degrees_sequence, chords_sequence, function_sequence
    ):
        detected = []
        # Ordena as sequências por tamanho decrescente
        sorted_targets = sorted(target_sequences, key=lambda x: -len(x))
        for target in sorted_targets:
            target_len = len(target)
            for i in range(len(degrees_sequence) - target_len + 1):
                window = tuple(degrees_sequence[i : i + target_len])  # noqa: E203
                if window == target:
                    # Usa a sequência de acordes originais para o campo "chords"
                    detected.append(
                        {
                            "type": "-".join(target),
                            "start_index": i,
                            "end_index": i + target_len - 1,
                            "chords": chords_sequence[i : i + target_len],  # noqa: E203
                            "functions": function_sequence[
                                i : i + target_len  # noqa: E203
                            ],  # Corrigido
                        }
                    )
        return detected

    @staticmethod
    def detect_secondary_dominants(harmonic_analysis):
        secondary_doms = []
        for i in range(len(harmonic_analysis) - 1):
            current = harmonic_analysis[i]
            next_chord = harmonic_analysis[i + 1]
            if current["function_code"] == "D2" and next_chord["degree"] in ["II", "V"]:
                secondary_doms.append(
                    {
                        "type": "Dominante secundário",
                        "chord": current["chord"],
                        "target": next_chord["degree"],
                    }
                )
        return secondary_doms

    @staticmethod
    def analyze_harmonic_flow(harmonic_analysis):
        analysis = {
            "tonic_resolutions": 0,
            "modal_borrowings": [],
            "secondary_dominants": [],
        }

        for i in range(len(harmonic_analysis) - 1):
            current = harmonic_analysis[i]
            next_chord = harmonic_analysis[i + 1]

            # Resoluções para tônica
            if next_chord["function_code"] == "T" and current["function_code"] in [
                "D",
                "SubV",
            ]:
                analysis["tonic_resolutions"] += 1

            # Empréstimos modais
            if current["function_code"] == "Emp":
                analysis["modal_borrowings"].append(
                    {
                        "chord": current["chord"],
                        "description": current["function_description"],
                    }
                )

            # Dominantes secundárias
            if current["function_code"] == "Dsec":
                analysis["secondary_dominants"].append(
                    {"chord": current["chord"], "target": next_chord["degree"]}
                )

        return analysis

    def analyze_progressions(self, harmonic_analysis):
        degrees_sequence = [entry["degree"] for entry in harmonic_analysis]
        chords_sequence = [entry["chord"] for entry in harmonic_analysis]
        function_sequence = [entry["function_code"] for entry in harmonic_analysis]

        # Detectar progressões por graus tonais
        degree_progressions = self.detect_progressions(
            PROGRESSIONS, degrees_sequence, chords_sequence, function_sequence
        )

        # Detectar progressões por funções
        function_progressions = self.detect_progressions(
            FUNCTION_PROGRESSIONS, function_sequence, chords_sequence, function_sequence
        )

        # Detectar dominantes secundários
        secondary_doms = self.detect_secondary_dominants(harmonic_analysis)

        # Categorizar as progressões
        categorized = {}
        for prog in degree_progressions + function_progressions:
            category = PROGRESSION_CATEGORIES.get(prog["type"], "Outra")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(prog)

        return [
            {
                "categories": categorized,
                "secondary_dominants": secondary_doms,
                "degree_progressions": degree_progressions,
                "function_progressions": function_progressions,
            }
        ]
