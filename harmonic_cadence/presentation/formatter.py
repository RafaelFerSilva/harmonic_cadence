# presentation/formatter.py

from collections import Counter
from typing import Dict, List, Set

from harmonic_cadence.domain.chord import Chord
from harmonic_cadence.domain.harmony import HarmonicAnalysis


class AnalysisFormatter:
    """
    Formata os resultados da análise harmônica para exibição.
    """

    @staticmethod
    def format_cifra_lines(cifra_lines: List[str]) -> str:
        """Formata as linhas da cifra para exibição."""
        result = ["Cifra:"]
        for line in cifra_lines:
            result.append(f"  {line}")
        return "\n".join(result)

    @staticmethod
    def format_unique_chords(chords: List[Chord]) -> str:
        """Formata a lista de acordes únicos encontrados e suas qualidades."""
        unique_chords = sorted(set(chord.symbol for chord in chords))
        qualities_counter = Counter()

        result = ["Acordes encontrados:"]
        for chord_symbol in unique_chords:
            chord = Chord(chord_symbol)
            qualities_counter[chord.quality] += 1
            result.append(f"  {chord_symbol}: {chord.quality}")

        result.append("\nDistribuição de qualidades:")
        for quality, count in qualities_counter.items():
            result.append(f"  {quality}: {count}")

        return "\n".join(result)

    @staticmethod
    def format_key_info(key: str, mode: str, chords: List[Chord]) -> str:
        """Formata informações sobre a tonalidade e razão de acordes menores."""
        unique_chords = set(chord.symbol for chord in chords)
        qualities_counter = Counter(
            Chord(chord_symbol).quality for chord_symbol in unique_chords
        )
        minor_ratio = (
            qualities_counter.get("minor", 0) / len(unique_chords)
            if unique_chords
            else 0
        )

        result = [
            f"Tonalidade sugerida: {key} {('maior' if mode == 'major' else 'menor')}",
            f"Razão de acordes menores (únicos): {minor_ratio:.2%}",
        ]
        return "\n".join(result)

    @staticmethod
    def format_harmonic_analysis(
        chords: List[Chord], analysis: HarmonicAnalysis
    ) -> str:
        """Formata a análise harmônica completa."""
        result = ["Análise harmônica (acordes únicos):"]
        result.append(
            "\nAcorde\t\tFunção\t\t\t\tDescrição\t\t\tQualidade\tOrigem do Empréstimo"
        )
        result.append("-" * 140)

        # Analisamos apenas acordes únicos para não repetir informações
        unique_chords = {}
        for i, chord in enumerate(chords):
            if chord.symbol not in unique_chords:
                prev_chord = chords[i - 1] if i > 0 else None
                next_chord = chords[i + 1] if i < len(chords) - 1 else None

                func_code, func_name, func_desc = analysis.analyze_function(
                    chord, prev_chord, next_chord
                )

                borrowing_source = "-"
                if func_code == "Emp":
                    borrowing_source = func_desc
                    func_desc = analysis.HARMONIC_FUNCTIONS["Emp"]["description"]

                unique_chords[chord.symbol] = {
                    "function": func_name,
                    "description": func_desc,
                    "quality": chord.quality,
                    "borrowing": borrowing_source,
                }

        for chord_symbol in sorted(unique_chords.keys()):
            info = unique_chords[chord_symbol]
            result.append(
                f"{chord_symbol:<12}\t"
                f"{info['function']:<28}\t"
                f"{info['description']:<28}\t"
                f"{info['quality']:<8}\t"
                f"{info['borrowing']}"
            )

        return "\n".join(result)

    @staticmethod
    def format_cadences(cadences: Dict[str, Set[str]]) -> str:
        """Formata as cadências encontradas."""
        result = ["Cadências encontradas:"]
        found_cadences = False

        for cadence_type, chord_pairs in cadences.items():
            if chord_pairs:
                found_cadences = True
                result.append(f"\n{cadence_type}:")
                for pair in sorted(chord_pairs):
                    result.append(f"  {pair}")

        if not found_cadences:
            result.append("Nenhuma cadência típica identificada.")

        return "\n".join(result)

    @staticmethod
    def format_complete_analysis(
        cifra_lines: List[str],
        chords: List[Chord],
        key: str,
        mode: str,
        analysis: HarmonicAnalysis,
        cadences: Dict[str, Set[str]],
    ) -> str:
        """Formata a análise completa em um único texto."""
        sections = [
            AnalysisFormatter.format_cifra_lines(cifra_lines),
            "",
            AnalysisFormatter.format_unique_chords(chords),
            "",
            AnalysisFormatter.format_key_info(key, mode, chords),
            "",
            AnalysisFormatter.format_harmonic_analysis(chords, analysis),
            "",
            AnalysisFormatter.format_cadences(cadences),
        ]

        return "\n".join(sections)
