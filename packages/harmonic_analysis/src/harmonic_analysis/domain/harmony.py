from collections import defaultdict
from typing import Dict, List, Literal, Optional, Tuple

from cifra_core.theory import Note
from cifra_core.theory import build_scale as theory_build_scale

from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.modal import _tetrad_quality, modal_degree
from harmonic_analysis.domain.constants import (
    DEGREES_MAJOR,
    DEGREES_MINOR,
    FUNCTION_PROGRESSIONS,
    HARMONIC_FUNCTIONS,
    MODE_NAMES_PT,
    PROGRESSION_CATEGORIES,
    PROGRESSIONS,
)

FunctionCode = Literal[
    "T", "SD", "D", "D2", "SubV", "Sub2", "Dsec", "Daux", "Emp", "Modal", "Dim",
    "Crom", "Outro"
]

# Grau cromático (com bemol) por offset de semitons da tônica — para nomear o
# alvo de um dominante auxiliar (empréstimo modal): bII, bIII, bVI, bVII, etc.
_CHROMATIC_DEGREE = {
    0: "I", 1: "bII", 2: "II", 3: "bIII", 4: "III", 5: "IV",
    6: "bV", 7: "V", 8: "bVI", 9: "VI", 10: "bVII", 11: "VII",
}

# Chaves de modo PT (legado, exibidas ao usuário) -> nomes do cifra_core.build_scale.
PT_TO_EN_MODE = {
    "maior": "major",
    "menor_natural": "minor",
    "menor_harmonica": "harmonic_minor",
    "menor_melodica": "melodic_minor",
    "dórico": "dorian",
    "frígio": "phrygian",
    "lídio": "lydian",
    "mixolídio": "mixolydian",
    "lócrio": "locrian",
}


class HarmonicAnalysis:
    """
    Realiza análise harmônica completa de uma progressão de acordes.
    """

    def __init__(
        self, key: str, mode: str = "major", church_mode: Optional[str] = None
    ):
        try:
            Note.parse(key)
        except Exception:
            raise ValueError(f"Tonalidade inválida: {key}") from None

        self.key = key
        self.mode = mode
        self.church_mode = church_mode  # modo de igreja ativo (Camada 2), se houver
        self.scale, self.scale_pcs, self.degrees = self._build_scale()
        self.HARMONIC_FUNCTIONS = HARMONIC_FUNCTIONS

    def _build_scale(self) -> Tuple[List[str], List[int], List[str]]:
        """Constrói a escala (com spelling correto) e seus graus via cifra_core.theory.

        Diferente da rotação de letras anterior, isto soletra os acidentes —
        Sol maior tem F#, Fá maior tem Bb — então graus de tonalidades com
        alterações passam a ser reconhecidos.
        """
        degrees = DEGREES_MAJOR if self.mode == "major" else DEGREES_MINOR
        notes = theory_build_scale(Note.parse(self.key), self.mode)
        return [str(n) for n in notes], [n.pitch_class for n in notes], degrees

    def roman_numeral(
        self, chord: Chord, next_chord: Optional[Chord] = None
    ) -> str:
        """Numeral romano do acorde (qualidade + inversão + aplicados)."""
        from harmonic_analysis.domain.roman import roman_numeral

        return roman_numeral(chord, self, next_chord)

    def get_degree(self, chord: Chord) -> Optional[str]:
        try:
            root_pc = Note.parse(chord.root).pitch_class
        except Exception:
            return None
        if root_pc in self.scale_pcs:
            degree = self.degrees[self.scale_pcs.index(root_pc)]
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

        # 0. Dominantes aplicados têm prioridade sobre a leitura diatônica por
        #    grau. Ordem (Chediak): I7/IV7 blues (XXXIV) → resolução funcional
        #    (XVIII: SubV2/auxiliar) → bVII7/bVI7 empréstimo sem resolução → V7/x
        #    secundário / SubV primário. A resolução precede a leitura de empréstimo
        #    de bVII7/bVI7: um Bb7/Ab7 que RESOLVE é dominante, não subdominante menor.
        if chord.is_dominant_seventh:
            pos = self._get_interval(self.key, chord.root)
            # 0a. I7/IV7 = blues (função especial fixa, Chediak XXXIV). Antes de tudo.
            if pos == 0:  # I7
                return (
                    "T",
                    "Tônica (I7 blues)",
                    "7ª sobre a tônica: função blues, não dominante (Chediak)",
                )
            if pos == 5:  # IV7
                return (
                    "SD",
                    "Subdominante (IV7 blues)",
                    "7ª sobre a subdominante: função blues, não dominante (Chediak)",
                )
            # 0b. Resolução funcional (Chediak XVIII, p.99) — precede bVII7/bVI7 Emp.
            if next_chord:
                ni = self._get_interval(chord.root, next_chord.root)
                target_is_tonic = self._get_interval(next_chord.root, self.key) == 0
                target_degree = self.get_degree(next_chord)
                # SubV7 secundário: fundamental ½t acima de um alvo DIATÔNICO não-tônica.
                if (
                    self._get_interval(next_chord.root, chord.root) == 1
                    and target_degree is not None
                    and not target_is_tonic
                ):
                    return (
                        "SubV",
                        f"SubV7 secundário (SubV7/{target_degree})",
                        "SubV7 de um grau diatônico, resolve ½t abaixo (Chediak p.99).",
                    )
                # Dominante auxiliar: resolve 5ª abaixo num alvo de EMPRÉSTIMO MODAL
                # (não-diatônico, não-tônica) — o alvo emprestado distingue do secundário.
                if ni == 5 and not target_is_tonic and target_degree is None:
                    alvo = _CHROMATIC_DEGREE[
                        self._get_interval(self.key, next_chord.root)
                    ]
                    return (
                        "Daux",
                        f"Dominante Auxiliar (V7/{alvo})",
                        self.HARMONIC_FUNCTIONS["Daux"]["description"],
                    )
            # 0c. bVII7/bVI7 SEM resolução funcional → subdominante menor (empréstimo).
            if pos == 10:  # bVII7
                return (
                    "Emp",
                    "Subdominante menor (bVII7)",
                    "bVII7: subdominante menor / empréstimo modal (Chediak)",
                )
            if pos == 8:  # bVI7
                return (
                    "Emp",
                    "Subdominante menor alterado (bVI7)",
                    "bVI7: subdominante menor alterado (Chediak)",
                )
            # 0d. V7/x secundário (alvo diatônico) e VII7 cadencial.
            if next_chord:
                ni = self._get_interval(chord.root, next_chord.root)
                target_is_tonic = self._get_interval(next_chord.root, self.key) == 0
                if ni == 5 and not target_is_tonic:
                    target_degree = self.get_degree(next_chord)
                    return (
                        "Dsec",
                        f"Dominante Secundário (V7/{target_degree})",
                        self.HARMONIC_FUNCTIONS["Dsec"]["description"],
                    )
                if pos == 11 and target_is_tonic:
                    return (
                        "D",
                        "VII7 cadencial",
                        "VII7 resolvendo direto na tônica: função cadencial (Chediak)",
                    )
            # 0e. SubV primário (bII7): um semitom acima da tônica.
            if self._get_interval(chord.root, self.key) == 11:
                return (
                    "SubV",
                    self.HARMONIC_FUNCTIONS["SubV"]["name"],
                    self.HARMONIC_FUNCTIONS["SubV"]["description"],
                )

        # 0c. Diminuto de 7ª como dominante SEM fundamental (V7(b9) rootless):
        #     B°7 (B-D-F-Ab) = G7(b9) (G-B-D-F-Ab) sem o G → dominante de C. A
        #     fundamental implícita está uma 3ª maior abaixo (root-4); a tônica de
        #     resolução, um semitom acima da fundamental escrita (Chediak, p. 90 —
        #     "diminutos equivalentes e relação com V7(9-)"). Só é dominante quando
        #     resolve no acorde um semitom acima; senão é diminuto de aproximação/
        #     passagem (cai na leitura diatônica/cromática abaixo).
        if chord.quality == "diminished" and next_chord:
            if self._get_interval(chord.root, next_chord.root) == 1:
                if self._get_interval(next_chord.root, self.key) == 0:
                    return (
                        "D",
                        "Dominante (°7 = V7(b9) de I)",
                        "Diminuto de 7ª = V7(b9) sem fundamental, resolvendo na "
                        "tônica (Chediak p. 90): tensão dominante, não repouso.",
                    )
                target_degree = self.get_degree(next_chord)
                return (
                    "Dsec",
                    f"Dominante Secundário (°7 = V7(b9)/{target_degree})",
                    "Diminuto de 7ª = V7(b9) sem fundamental — dominante rootless "
                    "do alvo um semitom acima (Chediak p. 90).",
                )

        # 0d. Diminuto de 7ª NÃO-dominante (não resolve ½t acima): classificado por
        #     TIPO (Chediak XXI-XXII, pp.102-104), nunca como empréstimo modal — um
        #     diminuto jamais é empréstimo (empréstimo é tríade/tétrade maior/menor de
        #     modo paralelo). O ascendente já saiu como dominante no 0c acima.
        if chord.quality == "diminished":
            if (
                prev_chord
                and next_chord
                and self._get_interval(prev_chord.root, next_chord.root) == 0
            ):
                return (
                    "Dim",
                    "Diminuto auxiliar",
                    "Bordadura: sai de um acorde e retorna a ele (Chediak pp.102-103).",
                )
            if next_chord and self._get_interval(next_chord.root, chord.root) == 1:
                return (
                    "Dim",
                    "Diminuto descendente",
                    "A fundamental desce um semitom para o próximo acorde "
                    "(Chediak pp.102-103).",
                )
            return (
                "Dim",
                "Diminuto",
                "Acorde diminuto conectivo / de passagem (Chediak pp.102-104).",
            )

        # 1. Função clássica diatônica (T, SD, D, Sub2, etc)
        for func_code, func_info in self.HARMONIC_FUNCTIONS.items():
            if degree in func_info["degrees"]:
                # Validações específicas para algumas funções
                if func_code == "Sub2":
                    # Exemplo: Substituto do IIm7 pode precisar de contexto (ex: próximo acorde)
                    if next_chord and self.get_degree(next_chord) in ["V", "V7"]:
                        return (func_code, func_info["name"], func_info["description"])
                    else:
                        continue  # Não é substituto se não preparar dominante

                # (O diminuto já é classificado no ramo 0d acima — por tipo, não por
                # grau —, então a seção 1 nunca mais o alcança.)

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

        # 5a. Função modal: se um modo está ativo e o acorde é diatônico a ele,
        #     é função modal (não empréstimo).
        if degree is None and self.church_mode:
            try:
                md = modal_degree(
                    Note.parse(chord.root).pitch_class, self.key, self.church_mode
                )
            except Exception:
                md = None
            if md is not None:
                return (
                    "Modal",
                    f"Função modal ({md})",
                    f"Diatônico ao modo {self.church_mode} de {self.key}",
                )

        # 5b. Empréstimo Modal
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
        """Identifica possíveis origens modais do acorde (modos paralelos da
        tônica), comparando por classe de altura — robusto à grafia (bemol ou
        sustenido). As notas exibidas vêm soletradas de `build_scale`."""
        try:
            root_pc = Note.parse(chord_root).pitch_class
            key_pc = Note.parse(self.key).pitch_class
        except Exception:
            return "Origem não identificada"
        if root_pc == key_pc:
            return "-"

        possible_sources = [
            mode_name
            for mode_name, en in PT_TO_EN_MODE.items()
            if root_pc
            in {n.pitch_class for n in theory_build_scale(Note.parse(self.key), en)}
        ]
        if not possible_sources:
            return "Origem não identificada"

        descriptions = []
        for mode_name in possible_sources:
            nome = MODE_NAMES_PT.get(mode_name, mode_name)
            scale = theory_build_scale(Note.parse(self.key), PT_TO_EN_MODE[mode_name])
            escala = " ".join(str(n) for n in scale)
            campo = self._build_harmonic_field(mode_name)
            descriptions.append(
                f"{nome} de {self.key}: [{escala}] | Campo harmônico: {campo}"
            )

        return " || ".join(descriptions)

    def _build_harmonic_field(self, mode_name: str) -> str:
        """Campo harmônico do modo, derivado da escala soletrada (`build_scale`)
        e da qualidade da tétrade por grau — correto por construção e com grafia
        enarmônica certa (Chediak, pp. 122-125)."""
        scale = theory_build_scale(Note.parse(self.key), PT_TO_EN_MODE[mode_name])
        degrees = DEGREES_MAJOR if mode_name == "maior" else DEGREES_MINOR
        return " | ".join(
            f"{deg}: {note}{_tetrad_quality(scale, i)}"
            for i, (deg, note) in enumerate(zip(degrees, scale))
        )

    def validate_chord(self, chord: Chord) -> bool:
        try:
            Note.parse(chord.root)
        except Exception:
            return False
        return True

    @staticmethod
    def _get_interval(note1: str, note2: str) -> int:
        """Intervalo ascendente em semitons (0..11), via classe de altura
        soletrada — enarmonicamente correto (`Bb` e `A#` dão o mesmo)."""
        return (Note.parse(note2).pitch_class - Note.parse(note1).pitch_class) % 12

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
