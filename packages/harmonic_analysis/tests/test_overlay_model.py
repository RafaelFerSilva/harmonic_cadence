"""Camada C — LM de sequência funcional (Witten-Bell).

Testa as três invariantes da spec `functional-anomaly-overlay`:
- suavização nunca produz P=0 (surpresa finita, mesmo contexto/função não visto);
- determinismo (mesmo corpus → mesma ordenação);
- fronteira de música respeitada (n-grama não cruja entre sequências).
"""

import math

from harmonic_analysis.overlay.model import FunctionalSequenceModel

# Corpus-brinquedo: "gramática" tonal simples repetida + uma frase rara.
_COMMON = ["T", "SD", "D", "T"]
_CORPUS = [_COMMON * 3, _COMMON * 3, ["T", "SD", "D", "T", "Dim", "Outro"]]


def _model(order=3):
    return FunctionalSequenceModel(order=order).fit(_CORPUS)


def test_smoothing_never_zero_probability():
    """Função nunca vista após um contexto ainda recebe surpresa FINITA."""
    m = _model()
    # 'Crom' nunca aparece no corpus; contexto arbitrário
    s = m.surprise_of(["T", "SD", "Crom"], 2)
    assert math.isfinite(s.surprise_bits)
    assert s.surprise_bits > 0


def test_unseen_context_backs_off():
    """Contexto trigrama inédito desce para bigrama/unigrama sem estourar."""
    m = _model()
    s = m.surprise_of(["Dim", "Outro", "T"], 2)  # 'Dim Outro' → 'T' inédito como trio
    assert math.isfinite(s.surprise_bits)


def test_rare_is_more_surprising_than_common():
    """A frase rara ('Dim','Outro') deve ser mais surpreendente que o T→SD→D comum."""
    m = _model()
    common = m.surprise_of(_COMMON, 2).surprise_bits          # D após T,SD (frequente)
    rare = m.surprise_of(["T", "SD", "D", "T", "Dim"], 4).surprise_bits  # Dim após D,T
    assert rare > common


def test_determinism():
    """Mesmo corpus, dois treinos → escores idênticos."""
    a = _model().surprise_of(_COMMON, 2).surprise_bits
    b = _model().surprise_of(_COMMON, 2).surprise_bits
    assert a == b


def test_song_boundary_not_crossed():
    """O contexto de uma música não vaza para a próxima.

    Se o n-grama cruzasse fronteiras, 'T' (fim de uma seq) e 'T' (início da
    próxima) formariam um bigrama espúrio. Treinamos com fronteira e sem, e a
    contagem de bigramas T→T deve refletir só o interno.
    """
    boundary = FunctionalSequenceModel(order=2).fit([["SD", "T"], ["T", "SD"]])
    # 'T'→'T' NUNCA ocorre dentro de uma música: contagem do bigrama = 0
    assert boundary._counts[2].get(("T", "T"), 0) == 0


def test_context_is_causal_and_bounded():
    """A posição i usa no máximo order-1 funções ANTERIORES (nunca futuras)."""
    m = _model(order=3)
    s = m.surprise_of(["T", "SD", "D", "T"], 3)
    assert s.context == ("SD", "D")  # 2 anteriores, ordem causal


def test_first_token_uses_empty_context():
    """A 1ª ocorrência de uma música cai no unigrama (contexto vazio)."""
    m = _model()
    s = m.surprise_of(["T", "SD"], 0)
    assert s.context == ()
    assert math.isfinite(s.surprise_bits)
