from typing import Dict, Type

from .base import ReportGenerator
from .html import HTMLReportGenerator
from .json import JSONReportGenerator
from .markdown import MarkdownReportGenerator


class ReportFactory:
    """Fábrica para criar geradores de relatório."""

    _generators: Dict[str, Type[ReportGenerator]] = {
        "markdown": MarkdownReportGenerator,
        "html": HTMLReportGenerator,
        "json": JSONReportGenerator,
    }

    @classmethod
    def create(cls, format_type: str) -> ReportGenerator:
        generator_class = cls._generators.get(format_type.lower())
        if not generator_class:
            raise ValueError(
                f"Formato '{format_type}' não suportado. "
                f"Formatos disponíveis: {', '.join(cls._generators.keys())}"
            )
        return generator_class()
