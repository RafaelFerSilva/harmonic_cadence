## Context

`_agglomerate` hoje funde os dois clusters de menor distância *average-linkage* (1 − média das
similaridades entre membros). Toda a matriz de similaridade já é computada; trocar a função de
ligação é trocar uma linha (média → máximo de distância = mínimo de similaridade). 293 músicas →
custo idêntico.

## Goals / Non-Goals

**Goals:**
- Oferecer `complete-linkage` como lente alternativa (partição mais equilibrada) sem trocar mais nada.
- Manter `average` como padrão (compatível); determinismo; sem dep nova.

**Non-Goals:**
- NÃO Ward (precisa de centróides/variância euclidiana — mal-definido sobre cosseno; follow-up).
- NÃO escolher linkage "ótimo" automaticamente (seria placar).
- NÃO mudar embedding, medoid, materialização ou schema.

## Decisions

**D1 — `complete` = 1 − min(sim entre membros).** *Average* usa a média; *complete* usa o pior par
(máxima distância). Complete penaliza clusters "espalhados", então quebra o núcleo em famílias
compactas — exatamente o que o usuário quer como alternativa. Ambos reusam `sim` já computado.
*Alternativa:* single-linkage (mínimo) — rejeitado: encadeia (chaining), agrava o mega-cluster.

**D2 — `linkage` como parâmetro (`average` default).** Preserva o comportamento atual; a CLI expõe
`--linkage`. Determinismo mantido pelo mesmo desempate (menor `song_id`).

**D3 — a função de ligação é injetada em `_agglomerate`.** Uma pequena função `link(ca, cb)` que
agrega as similaridades par-a-par (mean vs. min) — o laço de fusão não muda.

## Risks / Trade-offs

- **[Complete pode fragmentar demais em k alto]** → Mitigação: é escolha do usuário; ambas as lentes
  ficam disponíveis; a saída reporta o linkage e os tamanhos (denominador visível).
- **[Expectativa de "linkage certo"]** → Mitigação: spec/CLI declaram que é descritivo, sem "ótimo".

## Migration Plan

1. Só código; `average` é o default → zero mudança de comportamento sem `--linkage`. Rollback trivial.

## Open Questions

- **Ward/centroid linkage:** follow-up; exigiria uma métrica euclidiana sobre os vetores (ou
  aproximação), fora do escopo desta change.
