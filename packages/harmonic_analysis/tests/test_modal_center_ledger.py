"""Ledger de centro modal — cobertura + divergência, NÃO acurácia (D6).

Nada é detectado: o centro modal é fato citado. O ledger quantifica o gap entre a
leitura tonal do arranjo e a concepção de Chediak, usando o intervalo CURADO
(`finalis_from_tonal`), nunca subtração absoluta cross-fonte — logo é
transposição-seguro.
"""

from harmonic_analysis.corpus import CORPUS
from harmonic_analysis.corpus.modal_centers import Citation, ModalCenterFact
from harmonic_analysis.validation import modal_center_ledger


def test_ledger_covers_the_whole_curated_corpus():
    rows = modal_center_ledger(detected_centers={})
    assert len(rows) == len(CORPUS)
    # Cobertura honesta: detecção ausente vira None, nunca um palpite.
    assert all(r.detected_tonal_center is None for r in rows)


def test_ledger_carries_curated_interval_and_page():
    # Arrastão: centro tonal detectado Ré (pc 2); finalis curado +7 (Lá).
    arrastao = next(f for f in CORPUS if f.song == "Arrastao")
    rows = modal_center_ledger(detected_centers={arrastao.key: 2})
    row = next(r for r in rows if r.song == "Arrastao")
    assert row.finalis_from_tonal == 7
    assert row.page == 125
    assert row.curated_mode == "dorian"
    # finalis implícito = centro detectado + intervalo curado = 2 + 7 = 9 (Lá).
    assert row.implied_finalis_pc == 9


def test_ledger_is_transposition_safe():
    # Um único fato fabricado; finalis curado +7 (uma 5ªJ acima do centro tonal).
    fact = ModalCenterFact(
        artist="X", song="Y", curated_center="A", curated_mode="dorian",
        finalis_from_tonal=7,
        citation=Citation(source="Almir Chediak", volume=1, page=1),
    )
    # Transpor o ARRANJO inteiro por +5 desloca o centro detectado de 2 para 7…
    row_a = modal_center_ledger({fact.key: 2}, corpus=[fact])[0]
    row_b = modal_center_ledger({fact.key: 7}, corpus=[fact])[0]
    # …mas o intervalo curado NÃO muda (não é subtração absoluta cross-fonte).
    assert row_a.finalis_from_tonal == row_b.finalis_from_tonal == 7
    # …e o finalis implícito anda JUNTO com o arranjo (transposição-seguro).
    assert row_a.implied_finalis_pc == 9   # 2 + 7
    assert row_b.implied_finalis_pc == 2   # (7 + 7) % 12
