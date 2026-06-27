## Context

A v1 (`tonal-center-detection`) desempata a confusão **relativa** na banda de
quase-empate do K-S. A **paralela** (mesma tônica, modo trocado) é diferente em dois
aspectos, descobertos na exploração sobre o n=60:

1. O K-S erra a paralela **com confiança** — a tônica está certa, mas o modo errado,
   e o par paralelo costuma ficar **fora** da banda de empate (ex.: *Valsinha* Dó
   menor é o 3º candidato do K-S, score ~0.49 vs Dó maior ~0.63). Logo o desempate da
   v1 não a alcança.
2. A **cadência não distingue** maior de menor paralelos: `G7` é a dominante de Dó
   maior e de Dó menor; `A7→D` resolve em Ré maior e menor. O sinal discriminante é a
   **qualidade dos acordes de tônica** (Chediak: a 3ª da tônica define o modo).

Simulação (n=60): uma correção de modo guiada pelo voto de qualidade da tônica,
fechada pelo gate de âncora-baixo, dá modo 67%→83%, exata 50%→62%, relativa 62%→72%,
sem quebrar resposta correta.

## Goals / Non-Goals

**Goals:**

- Corrigir a confusão de modo paralelo na tônica em que a peça repousa.
- Não tocar casos de confusão relativa (tônica impostora) — o gate de âncora protege.
- Preservar o contrato do `KeyEstimate` e a Sina/gate sintético.

**Non-Goals:**

- Override cego do K-S por blend ponderado (arriscava regressão; a correção dirigida
  é mais segura e rendeu mais).
- Segmentar modulações reais (Wave/Chega) como regiões — follow-up de apresentação.
- Tunar o EPS da banda da v1.

## Decisions

**1. Corrigir o MODO, não re-rankear o tom.**
Na paralela a tônica já está certa; só o modo erra. Corrigir só o modo (mantendo a
tônica) é cirúrgico e não interfere no desempate relativo da v1. As duas etapas
compõem: a v1 acerta o **tom** (na banda), esta acerta o **modo** (na âncora).

**2. Sinal = voto de qualidade dos acordes de tônica.**
Sobre os acordes cuja **fundamental** é a tônica detectada, soma +1 (menor) / −1
(maior). Líquido ≥ +2 → menor; ≤ −2 → maior. A cadência não serve aqui (dominante
comum); a qualidade da tônica é o discriminante teórico do modo. Alternativa
(prevalência da 3ª no histograma): rejeitada — é o que o K-S já pesa e já erra.

**3. Gate de âncora-baixo (o que torna seguro).**
Só corrige se a tônica detectada é a **âncora tonal**: o último baixo é a tônica
**ou** há cadência autêntica (V/SubV → tônica) perto do fim. Isto reusa a lição da
Sina e da v1 (o baixo ancora o tom) e impede inverter o modo de uma tônica impostora
de confusão relativa. Concretamente: *Papel Marché* (detectada Lá menor, mas cadência
em Dó) **não** é âncora em Lá → fica intocada; *Valsinha* (assenta em Dó menor) →
corrige.

**4. Limiar = 2, robusto.**
Varredura no n=60: limiar 1 e 2 dão idêntico (83/62/72); 3 rende menos. 2 exige mais
que um empréstimo isolado (um `i` de passagem num tom maior não inverte). Num bloco
nomeado, recalibrável.

**5. Pós-processo dentro de `detect_key`.**
A correção roda depois do desempate de banda, sobre `(best_tonic, best_mode)`; se o
modo vira, o `score` reportado passa a ser o do par corrigido (consistência). Todos
os consumidores herdam a correção; o contrato não muda.

## Risks / Trade-offs

- **[Inverter o modo de um tom maior com empréstimos menores]** (ex.: maior com
  `IVm`/`i` de passagem) → Mitigação: o limiar 2 (net de 2 tônicas menores) e o gate
  de âncora; no n=60 nenhuma resposta correta quebrou.
- **[Gold ambíguo nas modulações]** Wave/Chega assentam em **maior** no fim mas o CC
  rotula **menor** (começam menor) — a correção "acerta" o gold invertendo p/ menor,
  mas a leitura honesta é multi-região. → Aceito como ganho de métrica aqui;
  registrado como follow-up de segmentação. Uma lateral (*Fotografia*) que de fato
  assenta na relativa é defensável.
- **Trade-off:** mais uma etapa em `detect_key` (reparse dos símbolos) — custo
  irrelevante (detecção não é hot path).

## Open Questions

- A correção e a v1 poderiam compartilhar um único passe que computa roots/basses/
  quals uma vez (hoje `cadence_corroboration` e a correção reparseiam). Refator de
  performance/limpeza, não funcional — candidato a follow-up se o reparse incomodar.
