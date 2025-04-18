import json
import sys
import unicodedata
from typing import Optional

from harmonic_cadence.infra.cifra_api import fetch_song_data
from harmonic_cadence.presentation.reports.factory import ReportFactory
from harmonic_cadence.services.analysis_service import AnalysisService


def print_header():
    print("=" * 80)
    print("Análise Harmônica de Músicas".center(80))
    print("=" * 80)
    print()


def format_input(text: str) -> str:
    text = text.strip().lower()
    text = text.replace(" ", "-")
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text


def get_input(prompt: str, default: str = "") -> str:
    value = input(f"{prompt}: ").strip()
    if not value:
        return default
    return format_input(value)


def validate_input(value: Optional[str], field_name: str) -> str:
    while not value:
        print(f"Por favor, informe {field_name.lower()}.")
        value = get_input(field_name)
    return value


def main():
    try:
        print_header()
        service = AnalysisService()

        # Processa argumentos de linha de comando
        output_format = "console"  # padrão
        for arg in sys.argv[1:]:
            if arg in ("--json", "-j"):
                output_format = "json"
            elif arg in ("--markdown", "-m"):
                output_format = "markdown"
            elif arg in ("--html", "-h"):
                output_format = "html"

        artist = validate_input(get_input("Artista"), "o artista")
        song = validate_input(get_input("Música"), "a música")

        print("\nAnalisando... Por favor, aguarde.\n")

        # Obtém os dados estruturados
        data = fetch_song_data(artist, song)
        result_structured = service.analyze_song_data_structured(data)

        # Gera o relatório no formato desejado
        if output_format == "json":
            print(json.dumps(result_structured, ensure_ascii=False, indent=2))
        elif output_format == "markdown":
            generator = ReportFactory.create("markdown")
            filename = generator.generate(result_structured)
            print(f"Relatório Markdowngerado em: {filename}")
        elif output_format == "html":
            generator = ReportFactory.create("html")
            filename = generator.generate(result_structured)
            print(f"Relatório HTML gerado em: {filename}")
        else:
            # Saída padrão para console
            result = service.analyze_song_data(data)
            print(result)

    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
