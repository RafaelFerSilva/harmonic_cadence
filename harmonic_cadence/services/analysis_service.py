# services/analysis_service.py

from typing import Any, Dict, List

from harmonic_cadence.domain.cadence import analyze_cadences
from harmonic_cadence.domain.chord import Chord, ChordPattern
from harmonic_cadence.domain.harmony import HarmonicAnalysis
from harmonic_cadence.infra.cifra_api import fetch_song_data
from harmonic_cadence.infra.utils import filter_cifra_lines
from harmonic_cadence.presentation.formatter import AnalysisFormatter


class AnalysisService:
    """
    Serviço principal que coordena a análise harmônica completa.
    """

    def __init__(self):
        self.formatter = AnalysisFormatter()

    def analyze_song_from_api(self, artist: str, song: str) -> str:
        """
        Realiza análise completa de uma música a partir da API.
        """
        try:
            # Busca dados da API
            data = fetch_song_data(artist, song)
            return self.analyze_song_data(data)
        except Exception as e:
            return f"Erro ao analisar música: {str(e)}"

    def analyze_song_data(self, data: Dict[str, Any]) -> str:
        """
        Realiza análise completa dos dados de uma música.
        """
        try:
            # Extrai informações básicas
            name = data.get("name", "Desconhecido")
            artist = data.get("artist", "Desconhecido")
            cifra_lines = data.get("cifra", [])

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
                chords=all_chords,
                key=key,
                mode=mode,
                analysis=analysis,
                cadences=cadences,
            )

        except Exception as e:
            return f"Erro durante a análise: {str(e)}"

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
