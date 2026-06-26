import json
import os
from datetime import datetime
from typing import Any, Dict

from .base import ReportGenerator


class JSONReportGenerator(ReportGenerator):
    def generate(self, analysis: Dict[str, Any], filename: str = None) -> str:
        directory = "report_json"
        os.makedirs(directory, exist_ok=True)

        if not filename:
            filename = self._generate_safe_filename(
                analysis["artist"], analysis["name"], "json"
            )

        full_path = os.path.join(directory, filename)

        # Cálculo de estatísticas
        total_chords = sum(analysis["chord_qualities"].values())
        major = analysis["chord_qualities"].get("major", 0)
        minor = analysis["chord_qualities"].get("minor", 0)
        major_pct = (major / total_chords * 100) if total_chords else 0
        minor_pct = (minor / total_chords * 100) if total_chords else 0

        # Link para YouTube
        yt_query = f"{analysis['artist']} {analysis['name']}".replace("-", " ")
        yt_link = (
            f"https://www.youtube.com/results?search_query={yt_query.replace(' ', '+')}"
        )

        # Estrutura do relatório JSON
        report = {
            "metadata": {
                "artist": analysis["artist"],
                "song": analysis["name"],
                "generated_at": datetime.now().isoformat(),
                "source": "CifraClub",
                "youtube_search": yt_link,
            },
            "key_analysis": {
                "suggested_key": analysis["key"],
                "mode": analysis["mode"],
            },
            "statistics": {
                "total_chords": total_chords,
                "major_chords": {"count": major, "percentage": round(major_pct, 1)},
                "minor_chords": {"count": minor, "percentage": round(minor_pct, 1)},
                "unique_chords": {
                    "count": len(analysis["unique_chords"]),
                    "chords": sorted(analysis["unique_chords"]),
                },
            },
            "harmonic_analysis": [
                {
                    "chord": item["chord"],
                    "degree": item["degree"],
                    "quality": item["quality"],
                    "strength": item.get("strength"),
                    "function": item["function"],
                    "function_code": item["function_code"],
                    "function_description": item["function_description"],
                }
                for item in analysis["harmonic_analysis"]
            ],
            "analysis_progression": [
                {
                    "categories": item["categories"],
                    "secondary_dominants": item["secondary_dominants"],
                    "degree_progressions": item["degree_progressions"],
                    "function_progressions": item["function_progressions"],
                }
                for item in analysis["analysis_progression"]
            ],
            "function_stats": [
                {
                    "function_counts": item["function_counts"],
                    "common_transitions": item["common_transitions"],
                }
                for item in analysis["function_stats"]
            ],
            "cadences": self._process_cadences(analysis["cadences"]),
            "raw_data": {
                "cifra": analysis["cifra_lines"],
                "cifra_html": analysis.get("cifra_html", ""),
            },
            "diagnostics": analysis.get("diagnostics", []),
        }

        # Camada 2 (profundidade) e Camada 3 (inteligência): incluídas quando
        # presentes; seções ausentes/vazias são omitidas (não emitidas como null).
        depth = {}
        for key in (
            "tonal_regions",
            "modal_analysis",
            "roman_numerals",
            "voice_leading",
            "chord_scales",
        ):
            self._maybe_add(depth, key, analysis.get(key))
        if depth:
            report["depth"] = depth

        intelligence = {}
        for key in ("functional_parse", "reharmonizations", "explanation"):
            self._maybe_add(intelligence, key, analysis.get(key))
        if intelligence:
            report["intelligence"] = intelligence

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return full_path

    def _maybe_add(self, target: Dict[str, Any], key: str, value: Any) -> None:
        """Inclui a seção apenas se presente (omissão graciosa)."""
        if self._present(value):
            target[key] = value

    def _process_cadences(self, cadences: Dict[str, Any]) -> Dict[str, Any]:
        if not cadences:
            return {"found": False, "types": []}

        processed = {"found": True, "types": []}

        for cad_type, cad_list in cadences.items():
            cadence_type = {"name": cad_type, "progressions": []}

            for cadence in cad_list:
                for prog in cadence.split(","):
                    prog = prog.strip()
                    if "→" in prog:
                        parts = [p.strip() for p in prog.split("→")]
                        if len(parts) == 2:
                            cadence_type["progressions"].append(
                                {"from": parts[0], "to": parts[1]}
                            )
                        else:
                            cadence_type["progressions"].append(
                                {"progression": " → ".join(parts)}
                            )
                    else:
                        cadence_type["progressions"].append({"chord": prog})

            processed["types"].append(cadence_type)

        return processed
