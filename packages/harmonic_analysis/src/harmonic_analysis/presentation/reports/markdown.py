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

            # Camada 3: explicação pedagógica (prosa)
            f.write(self._generate_explanation(analysis))

            # Camada 2: profundidade musical
            f.write(self._generate_roman_numerals(analysis))
            f.write(self._generate_tonal_regions(analysis))
            f.write(self._generate_modal_analysis(analysis))
            f.write(self._generate_voice_leading(analysis))
            f.write(self._generate_chord_scales(analysis))

            # Camada 3: inteligência
            f.write(self._generate_functional_parse(analysis))
            f.write(self._generate_reharmonizations(analysis))

            # Rodapé
            f.write(self._generate_footer())

        return full_path

    def _generate_explanation(self, analysis: Dict[str, Any]) -> str:
        text = analysis.get("explanation")
        if not self._present(text):
            return ""
        return f"## Explicação\n\n{text}\n\n"

    def _generate_roman_numerals(self, analysis: Dict[str, Any]) -> str:
        romans = analysis.get("roman_numerals")
        if not self._present(romans):
            return ""
        return "## Cifragem romana\n\n" + " · ".join(romans) + "\n\n"

    def _generate_tonal_regions(self, analysis: Dict[str, Any]) -> str:
        regions = analysis.get("tonal_regions")
        if not self._present(regions):
            return ""
        lines = ["## Regiões tonais\n"]
        for r in regions:
            lines.append(
                f"- acordes {r['start']}–{r['end']}: **{r['key']}** "
                f"(score {r['score']:.2f})"
            )
        return "\n".join(lines) + "\n\n"

    def _generate_modal_analysis(self, analysis: Dict[str, Any]) -> str:
        modal = analysis.get("modal_analysis")
        if not self._present(modal):
            return ""
        cadences = modal.get("cadences") or []
        cad = (
            ", ".join(f"{a}→{b}" for a, b in cadences) if cadences else "nenhuma"
        )
        return (
            "## Análise modal\n\n"
            f"- Centro modal: **{modal['tonic']} {modal['mode']}**\n"
            f"- Cadências modais: {cad}\n\n"
        )

    def _generate_voice_leading(self, analysis: Dict[str, Any]) -> str:
        vl = analysis.get("voice_leading")
        if not self._present(vl):
            return ""
        lines = ["## Condução de vozes\n"]
        if vl.get("bass_line"):
            lines.append("- **Linha de baixo:** " + " → ".join(vl["bass_line"]))
        if vl.get("descending"):
            lines.append(f"- **Trechos descendentes:** {len(vl['descending'])}")
        if vl.get("pedals"):
            lines.append(f"- **Pedais:** {len(vl['pedals'])}")
        if vl.get("line_cliches"):
            lines.append(f"- **Line clichês:** {len(vl['line_cliches'])}")
        if len(lines) == 1:
            return ""
        return "\n".join(lines) + "\n\n"

    def _generate_chord_scales(self, analysis: Dict[str, Any]) -> str:
        scales = analysis.get("chord_scales")
        if not self._present(scales):
            return ""
        lines = [
            "## Escala-acorde e tensões\n",
            "| Acorde | Escala | Tensões | Avoid |",
            "|--------|--------|---------|-------|",
        ]
        for cs in scales:
            tensions = ", ".join(cs.get("tensions", [])) or "-"
            avoid = ", ".join(cs.get("avoid", [])) or "-"
            lines.append(f"| {cs['chord']} | {cs['scale']} | {tensions} | {avoid} |")
        return "\n".join(lines) + "\n\n"

    def _generate_functional_parse(self, analysis: Dict[str, Any]) -> str:
        parse = analysis.get("functional_parse")
        if not self._present(parse) or not parse.get("chords"):
            return ""
        lines = [
            "## Parsing funcional (probabilístico)\n",
            "| Acorde | Função | Confiança | Alternativas |",
            "|--------|--------|-----------|--------------|",
        ]
        for c in parse["chords"]:
            alts = (
                ", ".join(
                    f"{a['function']} ({a['probability']:.0%})"
                    for a in c.get("alternatives", [])
                )
                or "-"
            )
            lines.append(
                f"| {c['chord']} | {c['function']} ({c['label']}) | "
                f"{c['confidence']:.0%} | {alts} |"
            )
        return "\n".join(lines) + "\n\n"

    def _generate_reharmonizations(self, analysis: Dict[str, Any]) -> str:
        from .base import REHARM_DISPLAY_LIMIT

        reharms = analysis.get("reharmonizations")
        if not self._present(reharms):
            return ""
        shown = reharms[:REHARM_DISPLAY_LIMIT]
        lines = ["## Sugestões de reharmonização\n"]
        for s in shown:
            original = " ".join(s["original"])
            result = " ".join(s["result"])
            lines.append(
                f"- **[{s['technique']}]** {original} → {result}  \n"
                f"  {s['rationale']}"
            )
        if len(reharms) > REHARM_DISPLAY_LIMIT:
            lines.append(
                f"\n*(+{len(reharms) - REHARM_DISPLAY_LIMIT} sugestões adicionais "
                "omitidas)*"
            )
        return "\n".join(lines) + "\n\n"

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
            "| Acorde | Grau | Qualidade | Força | Função | Código | Descrição |",
            "|--------|------|-----------|-------|--------|--------|-----------|",
        ]

        for item in analysis["harmonic_analysis"]:
            lines.append(
                f"| {item['chord']} | {item['degree'] or '-'} | {item['quality']} | "
                f"{item.get('strength') or '-'} | "
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
