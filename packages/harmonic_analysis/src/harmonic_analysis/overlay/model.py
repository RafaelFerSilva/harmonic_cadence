"""LM de sequência funcional com backoff suavizado (Witten-Bell).

Modelo estatístico **interpretável** sobre um vocabulário pequeno (as ~12 funções do
motor). Puro Python, SEM dependência de banco nem de ML pesado — treina de listas de
sequências (uma por música) e devolve a surpresa de cada ocorrência. Cada surpresa se
explica por contagens observáveis (denominador visível), não por pesos opacos.

Witten-Bell (Chen & Goodman 1998): para um contexto `c`,
    P(w|c) = λ_c · P_ML(w|c) + (1 − λ_c) · P(w | c[1:]),
    λ_c = N(c) / (N(c) + T(c)),
onde N(c) = ocorrências do contexto e T(c) = nº de continuações DISTINTAS vistas após
`c`. A recursão desce trigrama → bigrama → unigrama → uniforme (piso 1/|V|), então
nenhum contexto recebe P=0 (surpresa finita sempre). Determinístico: só contagem.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Surprise:
    """Escore de uma ocorrência — com os denominadores que o explicam."""

    function_code: str
    context: tuple[str, ...]  # histórico efetivo usado (até order-1 funções anteriores)
    surprise_bits: float      # -log2 P(função | contexto)
    ngram_count: int          # vezes que (contexto+função) foi visto no corpus
    context_count: int        # vezes que o contexto foi visto (N(c) no maior n aplicável)


class FunctionalSequenceModel:
    """N-grama suavizado (Witten-Bell) sobre códigos de função.

    `order=3` (trigrama) é o default — o probe mostrou cobertura de contexto
    excelente no corpus (99% da massa em contexto com contagem ≥10).
    """

    def __init__(self, order: int = 3) -> None:
        if order < 1:
            raise ValueError("order deve ser ≥ 1")
        self.order = order
        # counts[k][tuple-de-k] = contagem do k-grama (k = 1..order)
        self._counts: list[Counter] = [Counter() for _ in range(order + 1)]
        # por contexto de tamanho m (1..order-1): total N(c) e nº de tipos T(c)
        self._hist_total: list[dict] = [dict() for _ in range(order + 1)]
        self._hist_types: list[dict] = [dict() for _ in range(order + 1)]
        self._vocab: set[str] = set()
        self._fitted = False

    # ── treino ───────────────────────────────────────────────────────────────
    def fit(self, sequences) -> "FunctionalSequenceModel":
        """Treina de um iterável de sequências (cada uma = lista de function_code).

        Fronteira de música é respeitada: n-gramas NÃO cruzam sequências.
        """
        cont_types: list[dict] = [dict() for _ in range(self.order + 1)]
        for seq in sequences:
            seq = list(seq)
            self._vocab.update(seq)
            for k in range(1, self.order + 1):
                ck = self._counts[k]
                for i in range(len(seq) - k + 1):
                    gram = tuple(seq[i : i + k])
                    ck[gram] += 1
                    if k >= 2:
                        ctx, nxt = gram[:-1], gram[-1]
                        self._hist_total[k][ctx] = self._hist_total[k].get(ctx, 0) + 1
                        cont_types[k].setdefault(ctx, set()).add(nxt)
        for k in range(2, self.order + 1):
            self._hist_types[k] = {c: len(s) for c, s in cont_types[k].items()}
        self._fitted = True
        return self

    # ── probabilidade suavizada ──────────────────────────────────────────────
    def _p(self, word: str, context: tuple[str, ...]) -> float:
        """P(word | context) Witten-Bell recursivo. Nunca 0 (piso uniforme)."""
        m = len(context)
        if m == 0:
            uni = self._counts[1]
            total = sum(uni.values())
            types = len(uni)
            v = max(len(self._vocab), 1)
            if total == 0:
                return 1.0 / v
            lam = total / (total + types)
            return lam * (uni.get((word,), 0) / total) + (1 - lam) * (1.0 / v)
        k = m + 1  # ordem do n-grama completo
        n_ctx = self._hist_total[k].get(context, 0)
        backoff = self._p(word, context[1:])
        if n_ctx == 0:
            return backoff  # contexto nunca visto → desce um nível
        t_ctx = self._hist_types[k].get(context, 0)
        cnt = self._counts[k].get(context + (word,), 0)
        lam = n_ctx / (n_ctx + t_ctx)
        return lam * (cnt / n_ctx) + (1 - lam) * backoff

    # ── escore ───────────────────────────────────────────────────────────────
    def surprise_of(self, sequence, index: int) -> Surprise:
        """Surpresa da ocorrência em `sequence[index]` dado seu histórico causal."""
        if not self._fitted:
            raise RuntimeError("modelo não treinado — chame fit() antes")
        seq = list(sequence)
        word = seq[index]
        start = max(0, index - (self.order - 1))
        context = tuple(seq[start:index])
        p = self._p(word, context)
        bits = -math.log2(p) if p > 0 else float("inf")
        k = len(context) + 1
        return Surprise(
            function_code=word,
            context=context,
            surprise_bits=bits,
            ngram_count=self._counts[k].get(context + (word,), 0),
            context_count=(
                self._hist_total[k].get(context, 0)
                if context
                else sum(self._counts[1].values())
            ),
        )

    def score_sequence(self, sequence) -> list[Surprise]:
        """Surpresa de cada posição da sequência (contexto causal, sem cruzar música)."""
        seq = list(sequence)
        return [self.surprise_of(seq, i) for i in range(len(seq))]


class BidirectionalModel:
    """Surpresa BILATERAL sobre um canal — média das direções causal e reversa.

    Envolve dois `FunctionalSequenceModel`: um treinado esquerda→direita, outro sobre
    as sequências REVERTIDAS (direita→esquerda). A surpresa reversa da posição `i` de
    uma música é a surpresa da posição espelhada `L−1−i` na sequência revertida —
    então o contexto reverso é o que vem DEPOIS, sem cruzar fronteira de música (cada
    música é revertida isoladamente). O núcleo é agnóstico ao token, então isto serve
    igual para função e para grau.
    """

    def __init__(self, order: int = 3) -> None:
        self.order = order
        self.forward = FunctionalSequenceModel(order=order)
        self.backward = FunctionalSequenceModel(order=order)

    def fit(self, sequences) -> "BidirectionalModel":
        seqs = [list(s) for s in sequences]
        self.forward.fit(seqs)
        self.backward.fit([list(reversed(s)) for s in seqs])
        return self

    def surprise_bits(self, sequence, index: int) -> float:
        """Média (bits) da surpresa causal e reversa da posição `index`."""
        seq = list(sequence)
        fwd = self.forward.surprise_of(seq, index).surprise_bits
        rev = list(reversed(seq))
        bwd = self.backward.surprise_of(rev, len(seq) - 1 - index).surprise_bits
        return (fwd + bwd) / 2.0

    def score_sequence(self, sequence) -> list[float]:
        """Surpresa bilateral (bits) de cada posição da sequência."""
        seq = list(sequence)
        return [self.surprise_bits(seq, i) for i in range(len(seq))]
