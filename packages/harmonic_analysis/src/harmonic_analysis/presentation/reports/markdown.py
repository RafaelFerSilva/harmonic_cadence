import os
from datetime import datetime
from typing import Any, Dict

from .base import ReportGenerator


class MarkdownReportGenerator(ReportGenerator):
    """Gerador de relatórios em formato Markdown."""

    def get_extension(self) -> str:
        return "md"

    def generate(self, analysis: Dict[str, Any], filename: str = None) -> str:
        """Gera um relatório em formato Markdown."""

        directory = "report_markdown"
        os.makedirs(directory, exist_ok=True)

        if not filename:
            filename = self._generate_safe_filename(
                analysis["artist"], analysis["name"], "md"
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

        with open(full_path, "w", encoding="utf-8") as f:
            # Cabeçalho
            f.write(self._generate_header(analysis, yt_link))

            # Estatísticas
            f.write(
                self._generate_statistics(
                    total_chords, major, minor, major_pct, minor_pct, analysis
                )
            )

            # Cifra
            f.write(self._generate_cifra_section(analysis))

            # Análise harmônica
            f.write(self._generate_harmonic_analysis(analysis))

            # Cadências
            f.write(self._generate_cadences(analysis))

            # Rodapé
            f.write(self._generate_footer())

        return full_path

    def _generate_header(self, analysis: Dict[str, Any], yt_link: str) -> str:
        return (
            f"# Análise Harmônica\n\n"
            f"**Artista:** {analysis['artist']}\n\n"
            f"**Música:** {analysis['name']}\n\n"
            f"**Tonalidade sugerida:** {analysis['key']} ({analysis['mode']})\n\n"
            f"[🔊 Ouvir no YouTube]({yt_link})\n\n"
        )

    def _generate_statistics(
        self,
        total_chords: int,
        major: int,
        minor: int,
        major_pct: float,
        minor_pct: float,
        analysis: Dict[str, Any],
    ) -> str:
        return (
            "## Estatísticas Gerais\n"
            f"- **Total de acordes:** {total_chords}\n"
            f"- **Acordes maiores:** {major} ({major_pct:.1f}%)\n"
            f"- **Acordes menores:** {minor} ({minor_pct:.1f}%)\n"
            f"- **Acordes únicos:** {len(analysis['unique_chords'])}\n\n"
        )

    def _generate_cifra_section(self, analysis: Dict[str, Any]) -> str:
        lines = ["## Linhas da cifra\n```text"]
        lines.extend(line.rstrip() for line in analysis["cifra_lines"])
        lines.append("```\n\n")
        return "\n".join(lines)

    def _generate_harmonic_analysis(self, analysis: Dict[str, Any]) -> str:
        lines = [
            "## Análise harmônica dos acordes\n",
            "| Acorde | Grau | Qualidade | Função | Código | Descrição |",
            "|--------|------|-----------|--------|--------|-----------|",
        ]

        for item in analysis["harmonic_analysis"]:
            lines.append(
                f"| {item['chord']} | {item['degree'] or '-'} | {item['quality']} | "
                f"{item['function'] or '-'} | {item['function_code'] or '-'} | "
                f"{item['function_description'] or '-'} |"
            )

        return "\n".join(lines) + "\n\n"

    def _generate_cadences(self, analysis: Dict[str, Any]) -> str:
        lines = ["## Cadências encontradas\n"]

        if analysis["cadences"]:
            for cad_type, cad_list in analysis["cadences"].items():
                lines.append(f"### {cad_type}")
                for cadence in cad_list:
                    progressions = [prog.strip() for prog in cadence.split(",")]
                    for prog in progressions:
                        if "→" in prog:
                            before, after = prog.split("→")
                            lines.append(f"- {before.strip()} → {after.strip()}")
                        else:
                            lines.append(f"- {prog}")
                lines.append("")
        else:
            lines.append("Nenhuma cadência típica identificada.\n")

        return "\n".join(lines)

    def _generate_footer(self) -> str:
        return (
            "\n---\n"
            f"\n*Análise gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*\n"
        )
