import sys

from harmonic_cadence.services.analysis_service import AnalysisService


def print_header():
    """Imprime o cabeçalho do programa."""
    print("=" * 80)
    print("Análise Harmônica de Músicas".center(80))
    print("=" * 80)
    print()


def get_input(prompt: str, default: str = "") -> str:
    """Obtém entrada do usuário com valor padrão."""
    value = input(f"{prompt}: ").strip()
    return value if value else default


def main():
    """Função principal do programa."""
    try:
        print_header()

        # Inicializa o serviço
        service = AnalysisService()

        # Obtém dados da música
        artist = get_input("Artista")
        while not artist:
            print("Por favor, informe o artista.")
            artist = get_input("Artista")

        song = get_input("Música")
        while not song:
            print("Por favor, informe a música.")
            song = get_input("Música")

        # Realiza a análise
        print("\nAnalisando... Por favor, aguarde.\n")
        result = service.analyze_song_from_api(artist, song)

        # Exibe o resultado
        print(result)

    except KeyboardInterrupt:
        print("\nOperação cancelada pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
