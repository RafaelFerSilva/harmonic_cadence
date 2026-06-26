from abc import ABC, abstractmethod
from typing import Any, Dict

# Limite de sugestões de reharmonização exibidas por relatório (peças longas
# geram dezenas; mostramos as mais idiomáticas e sinalizamos o truncamento).
REHARM_DISPLAY_LIMIT = 12


class ReportGenerator(ABC):
    """Classe base abstrata para geradores de relatório."""

    @staticmethod
    def _present(value: Any) -> bool:
        """True se a seção deve ser renderizada (não-nula e não-vazia)."""
        return value is not None and value != [] and value != {} and value != ""

    @abstractmethod
    def generate(self, analysis: Dict[str, Any], filename: str = None) -> str:
        """
        Gera o relatório no formato específico.

        Args:
            analysis: Dicionário com os dados da análise
            filename: Nome do arquivo (opcional)

        Returns:
            str: Caminho do arquivo gerado
        """
        pass

    def _generate_safe_filename(self, artist: str, song: str, extension: str) -> str:
        """
        Gera um nome de arquivo seguro baseado no artista e música.
        """
        import unicodedata

        safe_name = f"{artist} - {song}".lower()
        safe_name = "".join(
            c
            for c in unicodedata.normalize("NFKD", safe_name)
            if c.isalnum() or c in ("-", "_", " ")
        )
        return f"{safe_name}.{extension}"
