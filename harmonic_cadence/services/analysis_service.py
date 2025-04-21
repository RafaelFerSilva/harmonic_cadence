from typing import Any, Counter, Dict, List

from harmonic_cadence.domain.cadence import analyze_cadences
from harmonic_cadence.domain.chord import Chord, ChordPattern
from harmonic_cadence.domain.harmony import HarmonicAnalysis
from harmonic_cadence.infra.cifra_api import fetch_song_data
from harmonic_cadence.infra.utils import filter_cifra_lines
from harmonic_cadence.presentation.formatter import AnalysisFormatter
from harmonic_cadence.utils.encoding import fix_encoding
from harmonic_cadence.utils.formatting import format_name


class AnalysisService:
    """
    Serviço principal que coordena a análise harmônica completa.
    """

    def __init__(self):
        self.formatter = AnalysisFormatter()

    def _normalize_text_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza o encoding e formata os campos textuais relevantes.
        """
        normalized = data.copy()

        # Normaliza e formata campos de texto simples
        normalized["name"] = format_name(fix_encoding(data.get("name", "Desconhecido")))
        normalized["artist"] = format_name(
            fix_encoding(data.get("artist", "Desconhecido"))
        )

        # Normaliza linhas da cifra
        cifra_lines = data.get("cifra", [])
        normalized["cifra"] = [fix_encoding(line) for line in cifra_lines]

        return normalized

    def _extract_chords(self, cifra_lines: List[str]) -> List[Chord]:
        """
        Extrai todos os acordes das linhas da cifra.
        """
        all_chords = []
        for line in cifra_lines:
            matches = ChordPattern.find_all(line)
            if matches:
                all_chords.extend([Chord(m) for m in matches])
        return all_chords

    def analyze_song_from_api(self, artist: str, song: str) -> str:
        """
        Realiza análise completa de uma música a partir da API.
        """
        try:
            # Busca dados da API
            data = fetch_song_data(artist, song)
            if not data or "error" in data:
                raise RuntimeError(f"Música não encontrada: {artist} - {song}")
            # Normaliza encoding e formatação dos dados
            data = self._normalize_text_data(data)
            return self.analyze_song_data(data)
        except Exception as e:
            return f"Erro ao analisar música: {str(e)}"

    def analyze_song_data(self, data: Dict[str, Any]) -> str:
        """
        Realiza análise completa dos dados de uma música.
        """
        try:
            # Normaliza encoding e formatação dos dados
            data = self._normalize_text_data(data)

            # Extrai informações básicas
            name = data.get("name", "Desconhecido")
            artist = data.get("artist", "Desconhecido")
            cifra_lines = data.get("cifra", [])
            cifra_html = data.get("cifra_html", "")

            # Filtra linhas indesejadas (tablaturas, marcações, etc.)
            cifra_lines = filter_cifra_lines(cifra_lines)

            print(f"\nAnalisando: {name} - {artist}\n")

            # Extrai acordes
            all_chords = self._extract_chords(cifra_lines)
            if not all_chords:
                return "Nenhum acorde encontrado na cifra."

            # Determina tonalidade
            key, mode = HarmonicAnalysis.guess_key(all_chords)
            if not key:
                return "Não foi possível determinar a tonalidade."

            # Cria analisador harmônico
            analysis = HarmonicAnalysis(key, mode)

            # Analisa cadências
            degree_seq = [analysis.get_degree(chord) or "-" for chord in all_chords]
            cadences = analyze_cadences(
                degree_seq, mode, [chord.symbol for chord in all_chords]
            )

            # Formata resultado completo
            return self.formatter.format_complete_analysis(
                cifra_lines=cifra_lines,
                cifra_html=cifra_html,
                chords=all_chords,
                key=key,
                mode=mode,
                analysis=analysis,
                cadences=cadences,
            )

        except Exception as e:
            return f"Erro durante a análise: {str(e)}"

    def analyze_song_data_structured(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retorna a análise em formato estruturado (dicionário), ideal para APIs ou frontends.
        """
        # Normaliza encoding e formatação dos dados
        # Validações iniciais
        if not data:
            raise RuntimeError("Dados da música não encontrados.")

        if "error" in data:
            raise RuntimeError(f"Erro nos dados da música: {data['error']}")

        if not data.get("cifra") or len(data["cifra"]) == 0:
            raise RuntimeError(
                f"Música não encontrada ou sem cifra: {data.get('artist')} - {data.get('name')}"
            )
        data = self._normalize_text_data(data)

        name = data.get("name", "Desconhecido")
        artist = data.get("artist", "Desconhecido")
        cifra_lines = data.get("cifra", [])
        cifra_html = data.get("cifra_html", "")
        cifra_lines = filter_cifra_lines(cifra_lines)

        all_chords = self._extract_chords(cifra_lines)
        key, mode = HarmonicAnalysis.guess_key(all_chords)
        analysis = HarmonicAnalysis(key, mode) if key else None
        degree_seq = (
            [analysis.get_degree(chord) or "-" for chord in all_chords]
            if analysis
            else []
        )
        cadences = (
            analyze_cadences(degree_seq, mode, [chord.symbol for chord in all_chords])
            if analysis
            else {}
        )

        harmonic_analysis = [
            {
                "chord": chord.symbol,
                "degree": analysis.get_degree(chord) if analysis else None,
                "quality": chord.quality,
                "function": analysis.analyze_function(chord)[1] if analysis else None,
                "function_code": (
                    analysis.analyze_function(chord)[0] if analysis else None
                ),
                "function_description": (
                    analysis.analyze_function(chord)[2] if analysis else None
                ),
            }
            for chord in all_chords
        ]

        analysis_progression = analysis.analyze_progressions(harmonic_analysis)
        function_stats = HarmonicAnalysis.analyze_function_stats(harmonic_analysis)

        return {
            "name": name,
            "artist": artist,
            "cifra_lines": cifra_lines,
            "cifra_html": cifra_html,
            "unique_chords": sorted(set(chord.symbol for chord in all_chords)),
            "chord_qualities": dict(Counter(chord.quality for chord in all_chords)),
            "key": key,
            "mode": mode,
            "harmonic_analysis": harmonic_analysis if analysis else [],
            "analysis_progression": analysis_progression if analysis else [],
            "function_stats": function_stats if analysis else [],
            "cadences": {k: list(v) for k, v in cadences.items()} if cadences else {},
        }
