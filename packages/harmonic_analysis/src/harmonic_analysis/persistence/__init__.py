"""Camada de persistência (persist-analysis-corpus).

Materializa a saída do motor num banco DuckDB que disseca toda a análise (do tom
às cadências), com grão na ocorrência de acorde. O banco é uma VIEW MATERIALIZADA
do motor — derivado, regenerável (`engine_version`), NUNCA fonte de verdade nem
gabarito de acurácia contra o qual o motor é medido.

Import tardio de `duckdb`: o núcleo (`cifra_core`, `harmonic_analysis.domain`) não
o importa; só o subcomando `corpus` e o materializador puxam esta camada.
"""

from harmonic_analysis.persistence.db import connect, init_db
from harmonic_analysis.persistence.materialize import build_corpus

__all__ = ["connect", "init_db", "build_corpus"]
