import re
from datetime import datetime
from typing import Any, Dict

from .base import ReportGenerator


class HTMLReportGenerator(ReportGenerator):
    def generate(self, analysis: Dict[str, Any], filename: str = None) -> str:
        if not filename:
            filename = self._generate_safe_filename(
                analysis["artist"], analysis["name"], "html"
            )

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

        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                self._generate_html_document(
                    analysis, yt_link, total_chords, major, minor, major_pct, minor_pct
                )
            )

        return filename

    def _process_cifra_line(self, line: str) -> str:
        chord_pattern = (
            r"\b([A-G](?:#|b)?(?:m|maj|min|dim|aug|sus)?"
            r"(?:[0-9]+)?(?:/[A-G][#b]?)?(?:\([^)]+\))?)\b"
        )

        if all(
            word.strip() == "" or re.match(chord_pattern, word) for word in line.split()
        ):
            processed_line = re.sub(chord_pattern, r'<b class="chord">\1</b>', line)
            return f'<div class="chord-line">{processed_line}</div>'
        else:
            processed_line = re.sub(chord_pattern, r'<b class="chord">\1</b>', line)
            return f'<div class="lyric-line">{processed_line}</div>'

    def _generate_cifra_section(self, cifra_lines: list) -> str:
        processed_lines = []
        for line in cifra_lines:
            if line.strip():
                processed_lines.append(self._process_cifra_line(line))
            else:
                processed_lines.append('<div class="empty-line">&nbsp;</div>')
        return "\n".join(processed_lines)

    def _generate_html_document(
        self, analysis, yt_link, total_chords, major, minor, major_pct, minor_pct
    ):
        # Processa as linhas da cifra
        cifra_content = self._generate_cifra_section(analysis["cifra_lines"])

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
    <style>
        :root {{
            --chord-color: #2D6CDF;
            --section-color: #666;
        }}

        body {{
            background: #f8f9fa;
            line-height: 1.5;
        }}

        @page {{
            size: A4;
            margin: 2.5cm 2cm 2.5cm 2cm;
        }}

        @page {{
            @top-center {{
                content: element(header);
            }}
            @bottom-center {{
                content: "Página " counter(page) " de " counter(pages);
                font-size: 0.95em;
                color: #888;
                border-top: 1px solid #ddd;
                padding-top: 0.2cm;
                margin-top: 0.5cm;
            }}
        }}

        #pdf-header {{
            position: running(header);
            text-align: center;
            font-size: 1.1em;
            color: #2D6CDF;
            border-bottom: 1px solid #ddd;
            padding-bottom: 0.2cm;
            margin-bottom: 0.5cm;
        }}

        .cifra-container {{
            display: flex;
            gap: 2rem;
            margin-top: 2rem;
        }}

        .cifra-column--left {{
            flex: 2;
            min-width: 0;
        }}

        .cifra-column--right {{
            flex: 1;
            min-width: 300px;
        }}

        .cifra-content {{
            font-family: 'Roboto Mono', monospace;
            background: #fff;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            font-size: 0.95rem;
            line-height: 1.6;
            overflow-x: auto;
        }}

        .chord-line {{
            color: var(--chord-color);
            font-weight: 500;
            padding: 0.2rem 0;
            white-space: pre;
        }}

        .lyric-line {{
            padding: 0.2rem 0;
            white-space: pre;
        }}

        .lyric-line .chord {{
            color: var(--chord-color);
            font-weight: 500;
        }}

        .empty-line {{
            height: 1rem;
        }}

        .section-name {{
            color: var(--section-color);
            font-weight: 500;
            margin-top: 1rem;
        }}

        @media (max-width: 768px) {{
            .cifra-container {{
                flex-direction: column;
            }}
            .cifra-column--right {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container py-4">
        <header class="pb-3 mb-4 border-bottom">
            <h1 class="display-5 fw-bold">Análise Harmônica de Música</h1>
        </header>

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

        <div class="cifra-container">
            <div class="cifra-column--left">
                <div class="cifra-content">
                    {cifra_content}
                </div>
            </div>

            <div class="cifra-column--right">
                <div class="card mb-4">
                    <div class="card-body">
                        <h2 class="h5 card-title">Estatísticas Gerais</h2>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">
                              Total de acordes: {total_chords}</li>
                            <li class="list-group-item">
                              Acordes maiores: {major} ({major_pct:.1f}%)</li>
                            <li class="list-group-item">
                              Acordes menores: {minor} ({minor_pct:.1f}%)</li>
                            <li class="list-group-item">
                              Acordes únicos: {len(analysis['unique_chords'])}</li>
                        </ul>
                    </div>
                </div>

                <div class="card">
                    <div class="card-body">
                        <h2 class="h5 card-title">Acordes únicos</h2>
                        <p class="card-text">{', '.join(analysis['unique_chords'])}</p>
                    </div>
                </div>
            </div>
        </div>

        {self._generate_analysis_section(analysis)}
        {self._generate_cadences_html(analysis)}

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
            # Extrai os valores para melhor legibilidade
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
          <div class="row mb-4">
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
            <div class="row mb-4">
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
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="h4">Cadências encontradas</h2>
                {''.join(cadences_html)}
            </div>
        </div>
        """
