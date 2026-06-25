import os
import re
from datetime import datetime
from typing import Any, Dict

from .base import ReportGenerator


def clean_whitespace(html: str) -> str:
    # Remove múltiplas quebras de linha e espaços em branco consecutivos
    html = re.sub(r'\n\s*\n+', '\n', html)  # múltiplas linhas vazias para uma linha
    return html.strip()


class HTMLReportGenerator(ReportGenerator):
    def generate(self, analysis: Dict[str, Any], filename: str = None) -> str:
        directory = "report_html"
        os.makedirs(directory, exist_ok=True)

        if not filename:
            filename = self._generate_safe_filename(
                analysis["artist"], analysis["name"], "html"
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
            f.write(
                self._generate_html_document(
                    analysis, yt_link, total_chords, major, minor, major_pct, minor_pct
                )
            )

        return full_path

    def _generate_html_document(
        self, analysis, yt_link, total_chords, major, minor, major_pct, minor_pct
    ):
        cifra_content = analysis.get("cifra_html", "")
        cifra_content = clean_whitespace(cifra_content)

        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise Harmônica - {analysis['artist']} - {analysis['name']}</title>
    <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
        rel="stylesheet"
    >
    <link
        href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap"
        rel="stylesheet"
    >
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --chord-color: #2D6CDF;
            --section-color: #666;
        }}

        body {{
            background: #f8f9fa;
            line-height: 1.6;
            font-family: 'Roboto Mono', monospace;
        }}

        /* Container da cifra com fundo e bordas */
        .cifra-content {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 3rem;
            overflow-x: auto;
        }}

        /* Espaçamento entre seções */
        .mb-5 {{
            margin-bottom: 3rem !important;
        }}

        /* Cards com estilo uniforme */
        .card {{
            border: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }}

        /* Títulos coloridos */
        .h4, .h5 {{
            color: var(--chord-color);
            margin-bottom: 1.2rem;
        }}

        /* Tabelas responsivas */
        .table-responsive {{
            border-radius: 8px;
            overflow: hidden;
        }}

        .table {{
            background: white;
        }}

        /* Responsividade */
        @media (max-width: 768px) {{
            .cifra-content {{
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container py-4">
        <header class="pb-3 mb-4 border-bottom">
            <h1 class="display-5 fw-bold">Análise Harmônica</h1>
        </header>

        <!-- Informações Gerais -->
        <div class="row mb-4">
            <div class="col-md-8">
                <h2 class="h4">Informações Gerais</h2>
                <p><strong>Artista:</strong> {analysis['artist']}</p>
                <p><strong>Música:</strong> {analysis['name']}</p>
                <p><strong>Tonalidade sugerida:</strong> {analysis['key']} ({analysis['mode']})</p>
                <a href="{yt_link}" target="_blank" class="btn btn-primary">
                    🔊 Ouvir no YouTube
                </a>
            </div>
        </div>

        <div class="cifra-content mb-5">
            {cifra_content}
        </div>

        <div class="row g-4 mb-5">

            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h2 class="h5 card-title">Acordes</h2>
                        <p class="card-text">{', '.join(analysis['unique_chords'])}</p>
                    </div>
                </div>
            </div>
        </div>

        {self._generate_analysis_section(analysis)}
        {self._generate_function_stats_html(analysis)}
        {self._generate_cadences_html(analysis)}
        {self._generate_progression_analysis(analysis)}

        <footer class="pt-3 mt-4 text-muted border-top">
            Análise gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        </footer>
    </div>
</body>
</html>
"""

    def _generate_analysis_section(self, analysis: Dict[str, Any]) -> str:
        rows = []
        for item in analysis["harmonic_analysis"]:
            chord = item["chord"]
            degree = item["degree"] or "-"
            quality = item["quality"]
            function = item["function"] or "-"
            function_code = item["function_code"] or "-"
            function_desc = item["function_description"] or "-"

            rows.append(
                f"""
                <tr>
                    <td>{chord}</td>
                    <td>{degree}</td>
                    <td>{quality}</td>
                    <td>{function}</td>
                    <td>{function_code}</td>
                    <td>{function_desc}</td>
                </tr>
            """
            )

        return f"""
            <div class="row mb-5">
                <div class="col-12">
                    <h2 class="h4">Análise harmônica dos acordes</h2>
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th>Acorde</th>
                                    <th>Grau</th>
                                    <th>Qualidade</th>
                                    <th>Função</th>
                                    <th>Código</th>
                                    <th>Descrição</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        """

    def _generate_cadences_html(self, analysis: Dict[str, Any]) -> str:
        if not analysis["cadences"]:
            return """
                <div class="row mb-5">
                    <div class="col-12">
                        <h2 class="h4">Cadências encontradas</h2>
                        <p>Nenhuma cadência típica identificada.</p>
                    </div>
                </div>
            """

        cadences_html = []
        for cad_type, cad_list in analysis["cadences"].items():
            progressions = []
            for cadence in cad_list:
                for prog in cadence.split(","):
                    prog = prog.strip()
                    if "→" in prog:
                        before, after = prog.split("→")
                        progressions.append(
                            f"<li>{before.strip()} → {after.strip()}</li>"
                        )
                    else:
                        progressions.append(f"<li>{prog}</li>")

            cadences_html.append(
                f"""
                <div class="cadence-section">
                    <h3 class="h5">{cad_type}</h3>
                    <ul class="list-unstyled">
                        {''.join(progressions)}
                    </ul>
                </div>
            """
            )

        return f"""
            <div class="row mb-5">
                <div class="col-12">
                    <h2 class="h4">Cadências encontradas</h2>
                    {''.join(cadences_html)}
                </div>
            </div>
        """

    def _generate_progression_analysis(self, analysis: Dict[str, Any]) -> str:
        if not analysis.get("analysis_progression"):
            return ""

        sections = []
        for item in analysis["analysis_progression"]:
            categories = item.get("categories", {})
            for category, progressions in categories.items():
                if not progressions:
                    continue

                progression_list = []
                for prog in progressions:
                    type_ = prog.get("type", "")
                    chords = " → ".join(prog.get("chords", []))
                    progression_list.append(
                        f"""
                        <li>
                            <strong>Tipo:</strong> {type_}<br>
                            <strong>Progressão:</strong> {chords}<br>
                        </li>
                    """
                    )

                sections.append(
                    f"""
                    <div class="card mb-3">
                        <div class="card-header">{category}</div>
                        <div class="card-body">
                            <ul class="list-unstyled">
                                {''.join(progression_list)}
                            </ul>
                        </div>
                    </div>
                """
                )

        return f"""
            <div class="row mb-5">
                <div class="col-12">
                    <h2 class="h4">Análise de Progressões Harmônicas</h2>
                    {''.join(sections)}
                </div>
            </div>
        """

    def _generate_function_stats_html(self, analysis: Dict[str, Any]) -> str:
        if not analysis.get("function_stats"):
            return ""

        stats = analysis["function_stats"][0]

        function_counts_html = []
        for func, data in stats["function_counts"].items():
            if isinstance(data, dict):
                count = data["count"]
                examples = ", ".join(data.get("example_chords", []))
                function_counts_html.append(
                    f"<tr><td>{func}</td><td>{count}</td><td>{examples}</td></tr>"
                )
            else:
                function_counts_html.append(
                    f"<tr><td>{func}</td><td>{data}</td><td>-</td></tr>"
                )

        transitions_html = []
        for trans, data in stats["common_transitions"].items():
            if isinstance(data, dict):
                count = data["count"]
                examples = ", ".join(data.get("example_progressions", []))
                transitions_html.append(
                    f"<tr><td>{trans}</td><td>{count}</td><td>{examples}</td></tr>"
                )
            else:
                transitions_html.append(
                    f"<tr><td>{trans}</td><td>{data}</td><td>-</td></tr>"
                )

        return f"""
            <div class="row mb-5">
                <div class="col-12">
                    <h2 class="h4">Estatísticas Funcionais</h2>

                    <div class="card mb-4">
                        <div class="card-header">Distribuição de Funções Harmônicas</div>
                        <div class="card-body">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Função</th>
                                        <th>Ocorrências</th>
                                        <th>Exemplos de Acordes</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join(function_counts_html)}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">Transições Mais Comuns</div>
                        <div class="card-body">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Transição</th>
                                        <th>Ocorrências</th>
                                        <th>Exemplos de Progressões</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join(transitions_html)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        """
