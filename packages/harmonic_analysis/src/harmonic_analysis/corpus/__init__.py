"""Corpora curados — fatos musicológicos citados, nunca detectados das cifras.

A fronteira de copyright vale aqui: só FATOS (música→centro→modo→página→nota),
NUNCA as harmonizações/cifras/tabelas da Parte 4 do Chediak.
"""

from harmonic_analysis.corpus.modal_centers import (
    CORPUS,
    Citation,
    ModalCenterFact,
    lookup_modal_center,
)
from harmonic_analysis.corpus.tritone_adjudications import (
    ADJUDICATIONS,
    TritoneVerdict,
    TritoneVerdictKind,
    lookup_tritone_verdict,
)

__all__ = [
    "CORPUS",
    "Citation",
    "ModalCenterFact",
    "lookup_modal_center",
    "ADJUDICATIONS",
    "TritoneVerdict",
    "TritoneVerdictKind",
    "lookup_tritone_verdict",
]
