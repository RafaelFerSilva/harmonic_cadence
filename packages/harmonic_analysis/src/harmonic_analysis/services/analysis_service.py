import re
from typing import Any, Counter, Dict, List

from cifra_core import ChordPattern, SongProvider, SongProviderError, fix_encoding
from cifra_core.theory import root_pitch_class

from harmonic_analysis.domain import chord_scale, voice_leading
from harmonic_analysis.domain.cadence import analyze_cadences
from harmonic_analysis.domain.chord import Chord
from harmonic_analysis.domain.harmony import HarmonicAnalysis
from harmonic_analysis.domain.key_detection import detect_key, segment_keys
from harmonic_analysis.domain.modal import detect_mode, modal_cadences, modal_degree
from harmonic_analysis.presentation.formatter import AnalysisFormatter
from harmonic_analysis.utils.formatting import format_name

MINOR_MODES = {"dorian", "phrygian", "aeolian", "locrian"}


class AnalysisService:
    """
    Serviço principal que coordena a análise harmônica completa.
    """

    def __init__(self, provider: SongProvider):
        self.provider = provider
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

    def remove_html_tags(self, text: str) -> str:
        clean = re.sub(r'<[^>]+>', '', text)
        return clean

    def _extract_chords(self, cifra_lines: List[str]) -> List[Chord]:
        all_chords = []
        for line in cifra_lines:
            clean_line = self.remove_html_tags(line)
            matches = ChordPattern.find_all(clean_line)
            if matches:
                all_chords.extend([Chord(m) for m in matches])
        return all_chords

    def _validate_input_data(self, data: Dict[str, Any]) -> Dict[str, Any] | None:
        if not data:
            return {"success": False, "error": "Dados da música não encontrados."}
        if "error" in data:
            return {
                "success": False,
                "error": f"Erro nos dados da música: {data['error']}",
            }
        if not data.get("cifra"):
            return {
                "success": False,
                "error": f"Música sem cifra: {data.get('artist', 'Artista desconhecido')} - {data.get('name', 'Nome desconhecido')}",
            }
        if isinstance(data.get("cifra"), list) and len(data["cifra"]) == 0:
            return {
                "success": False,
                "error": f"Cifra vazia: {data.get('artist', 'Artista desconhecido')} - {data.get('name', 'Nome desconhecido')}",
            }
        return None

    def _determine_key_and_mode(self, all_chords, data):
        try:
            estimate = detect_key([chord.symbol for chord in all_chords])
            key = estimate.key_note if estimate else None
            mode = estimate.mode if estimate else None
            if not key:
                partial_results = {
                    "name": data.get("name", "Desconhecido"),
                    "artist": data.get("artist", "Desconhecido"),
                    "unique_chords": sorted(set(chord.symbol for chord in all_chords)),
                    "chord_qualities": dict(
                        Counter(chord.quality for chord in all_chords)
                    ),
                }
                return (
                    None,
                    None,
                    partial_results,
                    "Não foi possível determinar a tonalidade.",
                )
            return key, mode, None, None
        except Exception as e:
            return None, None, None, f"Erro na determinação da tonalidade: {str(e)}"

    def _analyze_degrees(self, analysis, all_chords, data, key, mode):
        try:
            degree_seq = (
                [analysis.get_degree(chord) or "-" for chord in all_chords]
                if analysis
                else []
            )
            if analysis and not any(deg != "-" for deg in degree_seq):
                partial_results = {
                    "name": data.get("name", "Desconhecido"),
                    "artist": data.get("artist", "Desconhecido"),
                    "key": key,
                    "mode": mode,
                    "unique_chords": sorted(set(chord.symbol for chord in all_chords)),
                }
                return (
                    None,
                    "Não foi possível analisar os graus harmônicos dos acordes.",
                    partial_results,
                )
            return degree_seq, None, None
        except Exception as e:
            return None, f"Erro na análise de graus: {str(e)}", None

    def _detailed_harmonic_analysis(self, analysis, all_chords):
        harmonic_analysis = []
        try:
            for i, chord in enumerate(all_chords):
                try:
                    prev_chord = all_chords[i - 1] if i > 0 else None
                    next_chord = all_chords[i + 1] if i < len(all_chords) - 1 else None

                    if not analysis.validate_chord(chord):
                        harmonic_analysis.append(
                            {
                                "chord": chord.symbol,
                                "degree": None,
                                "quality": chord.quality,
                                "function_code": "Outro",
                                "function": "Acorde inválido",
                                "function_description": "Nota raiz inválida ou formato incorreto",
                            }
                        )
                        continue

                    chord_analysis = {
                        "chord": chord.symbol,
                        "degree": analysis.get_degree(chord) if analysis else None,
                        "quality": chord.quality,
                    }

                    if analysis:
                        function_result = analysis.analyze_function(
                            chord, prev_chord, next_chord
                        )
                        chord_analysis.update(
                            {
                                "function": (
                                    function_result[1]
                                    if len(function_result) > 1
                                    else None
                                ),
                                "function_code": (
                                    function_result[0]
                                    if len(function_result) > 0
                                    else None
                                ),
                                "function_description": (
                                    function_result[2]
                                    if len(function_result) > 2
                                    else None
                                ),
                            }
                        )

                    harmonic_analysis.append(chord_analysis)

                except Exception as e:
                    print(f"Aviso: Erro ao analisar acorde {chord.symbol}: {str(e)}")
                    harmonic_analysis.append(
                        {
                            "chord": chord.symbol,
                            "error": f"Não foi possível analisar: {str(e)}",
                        }
                    )
        except Exception as e:
            raise RuntimeError(f"Erro na análise harmônica detalhada: {str(e)}")

        return harmonic_analysis

    def _build_result(
        self,
        data,
        cifra_lines,
        all_chords,
        key,
        mode,
        harmonic_analysis,
        analysis_progression,
        function_stats,
        cadences,
    ):
        return {
            "success": True,
            "name": data.get("name", "Desconhecido"),
            "artist": data.get("artist", "Desconhecido"),
            "cifra_lines": cifra_lines,
            "cifra_html": data.get("cifra_html", ""),
            "unique_chords": sorted(set(chord.symbol for chord in all_chords)),
            "chord_qualities": dict(Counter(chord.quality for chord in all_chords)),
            "key": key,
            "mode": mode,
            "harmonic_analysis": harmonic_analysis,
            "analysis_progression": analysis_progression,
            "function_stats": function_stats,
            "cadences": {k: list(v) for k, v in cadences.items()} if cadences else {},
        }

    def analyze_song_data_structured(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Valida dados básicos
            validation_error = self._validate_input_data(data)
            if validation_error:
                return validation_error

            # Normaliza dados
            try:
                data = self._normalize_text_data(data)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro na normalização dos dados: {str(e)}",
                }

            # As linhas já chegam limpas do provider (contrato D3 — filtragem
            # canônica e idempotente vive no cifra_core, aplicada uma única vez).
            cifra_lines = data.get("cifra", [])
            if not cifra_lines:
                return {
                    "success": False,
                    "error": "Cifra não contém linhas válidas.",
                }

            # Extrai acordes
            try:
                all_chords = self._extract_chords(cifra_lines)
                if not all_chords:
                    return {
                        "success": False,
                        "error": "Nenhum acorde válido encontrado na cifra.",
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro na extração de acordes: {str(e)}",
                }

            # Determina tonalidade
            key, mode, partial_results, error = self._determine_key_and_mode(
                all_chords, data
            )
            if error:
                return {
                    "success": False,
                    "error": error,
                    "partial_results": partial_results,
                }

            # Cria analisador harmônico — quando um modo é detectado, usa a
            # tônica modal (o "final") e o modo ativo (Camada 2).
            mode_info = detect_mode([c.symbol for c in all_chords])
            if mode_info:
                key = mode_info.tonic
                mode = "minor" if mode_info.mode in MINOR_MODES else "major"
                analysis = HarmonicAnalysis(key, mode, mode_info.mode)
            elif key:
                analysis = HarmonicAnalysis(key, mode)
            else:
                analysis = None

            # Analisa graus harmônicos
            degree_seq, error, partial_results = self._analyze_degrees(
                analysis, all_chords, data, key, mode
            )
            if error:
                return {
                    "success": False,
                    "error": error,
                    "partial_results": partial_results,
                }

            # Analisa cadências
            try:
                cadences = (
                    analyze_cadences(
                        degree_seq, mode, [chord.symbol for chord in all_chords]
                    )
                    if analysis and degree_seq
                    else {}
                )
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Erro na análise de cadências: {str(e)}",
                }

            # Análise harmônica detalhada
            harmonic_analysis = self._detailed_harmonic_analysis(analysis, all_chords)

            # Análise de progressões
            analysis_progression = (
                analysis.analyze_progressions(harmonic_analysis) if analysis else []
            )

            # Estatísticas de funções
            function_stats = (
                analysis.analyze_function_stats(harmonic_analysis)
                if harmonic_analysis
                else []
            )

            # Monta resultado final
            result = self._build_result(
                data,
                cifra_lines,
                all_chords,
                key,
                mode,
                harmonic_analysis,
                analysis_progression,
                function_stats,
                cadences,
            )
            # Regiões tonais (detecção de modulação)
            try:
                result["tonal_regions"] = [
                    {
                        "start": r.start,
                        "end": r.end,
                        "key": r.estimate.name,
                        "score": r.estimate.score,
                    }
                    for r in segment_keys([chord.symbol for chord in all_chords])
                ]
            except Exception:
                result["tonal_regions"] = []

            # Camada 2: profundidade musical
            self._add_depth_sections(result, all_chords, analysis, mode_info)
            return result

        except Exception as e:
            raise RuntimeError(f"Erro crítico na análise da música: {str(e)}")

    def _add_depth_sections(self, result, all_chords, analysis, mode_info) -> None:
        """Popula as seções da Camada 2: modal, RNA, condução de vozes, escala-acorde."""
        # Análise modal
        try:
            if mode_info:
                md_seq = []
                for c in all_chords:
                    try:
                        md_seq.append(
                            modal_degree(
                                root_pitch_class(c.symbol),
                                mode_info.tonic,
                                mode_info.mode,
                            )
                        )
                    except Exception:
                        md_seq.append(None)
                result["modal_analysis"] = {
                    "tonic": mode_info.tonic,
                    "mode": mode_info.mode,
                    "cadences": modal_cadences(
                        [d for d in md_seq if d], mode_info.mode
                    ),
                }
            else:
                result["modal_analysis"] = None
        except Exception:
            result["modal_analysis"] = None

        # Cifragem romana
        try:
            result["roman_numerals"] = (
                [
                    analysis.roman_numeral(
                        c, all_chords[i + 1] if i + 1 < len(all_chords) else None
                    )
                    for i, c in enumerate(all_chords)
                ]
                if analysis
                else []
            )
        except Exception:
            result["roman_numerals"] = []

        # Condução de vozes
        try:
            result["voice_leading"] = voice_leading.analyze(all_chords)
        except Exception:
            result["voice_leading"] = {}

        # Escala-acorde e tensões
        try:
            result["chord_scales"] = (
                [
                    cs
                    for c in all_chords
                    if (cs := chord_scale.analyze_chord(c, analysis)) is not None
                ]
                if analysis
                else []
            )
        except Exception:
            result["chord_scales"] = []

    def analyze_song_from_api(self, artist: str, song: str) -> Dict[str, Any]:
        """
        Realiza análise completa de uma música obtida via SongProvider.
        """
        try:
            cifra = self.provider.get_song(artist, song)
        except SongProviderError as e:
            return {"success": False, "error": str(e)}
        return self.analyze_song_data_structured(cifra.to_dict())
