"""Camada C — overlay estatístico ML/NLP (subordinado ao símbolo).

Um overlay DESCRITIVO sobre o corpus persistido (`corpus.duckdb`, grão = ocorrência
de acorde). Treina um LM de sequência funcional suavizado sobre os `function_code`s
já rotulados pelo motor e computa a SURPRESA (-log2 P(função | contexto)) de cada
ocorrência, produzindo uma WORKLIST ranqueada de casos estatisticamente improváveis.

Lei de ferro (não-negociável): o overlay é **PRATA** — o ML **rankeia**, o Chediak
**adjudica**. Ele NUNCA reescreve `function_code`, NUNCA arbitra centro, NUNCA compete
com o ouro. Discordância entre a estatística e o rótulo do coder é **sinal de
curadoria**, não erro — é isso que legitima treinar/medir sobre a saída do próprio
motor sem cair em circularidade.

Import tardio de `duckdb`: o núcleo não o importa; só o subcomando `corpus anomalies`
e o materializador puxam esta camada.
"""

from harmonic_analysis.overlay.model import (
    BidirectionalModel,
    FunctionalSequenceModel,
)

__all__ = ["FunctionalSequenceModel", "BidirectionalModel"]
