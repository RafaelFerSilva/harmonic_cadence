import sys
from typing import Optional

from harmonic_cadence.services.analysis_service import AnalysisService


def print_header():
    """Imprime o cabeçalho do programa."""
    print("=" * 80)
    print("Análise Harmônica de Músicas".center(80))
    print("=" * 80)
    print()


def format_input(text: str) -> str:
    """
    Formata o texto de entrada substituindo espaços por hífens e
    removendo caracteres especiais.
    """
    # Remove espaços extras e converte para minúsculas
    text = text.strip().lower()

    # Substitui espaços por hífens
    text = text.replace(" ", "-")

    # Remove acentos e caracteres especiais (mantém letras, números e hífen)
    import unicodedata

    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")

    return text


def get_input(prompt: str, default: str = "") -> str:
    """
    Obtém entrada do usuário com valor padrão e formata adequadamente.
    """
    value = input(f"{prompt}: ").strip()
    if not value:
        return default
    return format_input(value)


def validate_input(value: Optional[str], field_name: str) -> str:
    """
    Valida e obtém entrada do usuário até que seja válida.
    """
    while not value:
        print(f"Por favor, informe {field_name.lower()}.")
        value = get_input(field_name)
    return value


def main():
    """Função principal do programa."""
    try:
        print_header()

        # Inicializa o serviço
        service = AnalysisService()

        # Obtém e valida dados da música
        artist = validate_input(get_input("Artista"), "o artista")
        song = validate_input(get_input("Música"), "a música")

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
