## Context

`harmonic-similarity-retrieval` já dá o embedding por música (`fingerprint_from_db`) e o cosseno
(`style_fingerprint.similarity`), materializando top-K vizinhos (`song_neighbor`). Falta o retrato
global: famílias + protótipos. Não há dependência numérica no projeto (numpy/scipy/sklearn ausentes,
por escolha) — o padrão é mecanismo interpretável em stdlib (n-grama Witten-Bell, cosseno por
contagem). 293 músicas é minúsculo: qualquer algoritmo O(n³) roda em ms.

## Goals / Non-Goals

**Goals:**
- Famílias harmônicas + música-protótipo (medoid), interpretáveis, transposição-invariantes.
- Reusar o embedding/cosseno existentes; **zero dependência nova**.
- Descritivo (não arbitra; família ≠ qualidade); zero regressão nos gates.

**Non-Goals:**
- NÃO escolher `k` automaticamente / alegar "k ótimo" (seria placar); `k` é do usuário.
- NÃO k-means/DBSCAN/embeddings aprendidos (exigiriam dep ou dado que não temos).
- NÃO visualização (dendrograma gráfico) — a hierarquia fica no algoritmo; a saída é textual.

## Decisions

**D1 — aglomerativo *average-linkage*, puro Python.** Sem dependência, interpretável, e produz uma
**hierarquia** (famílias e sub-famílias) que é musicologicamente natural. 293 pontos → merges O(n³)
naive ≈ 25M ops, trivial. *Alternativa:* k-means (precisa de centróides num espaço denso e de `k`
fixo com reinícios aleatórios — menos determinístico, menos interpretável) ou community detection no
grafo k-NN (precisa de lib ou custom, e o k-NN esparso perde estrutura) — rejeitados.

**D2 — vetor sobre eixo de funções GLOBAL, não par-a-par.** Para clusterizar, todos os vetores
precisam viver no MESMO espaço; então construo o eixo global (união de todas as funções do corpus,
≤12) e vetorizo cada música uma vez (`_feature_vector` sobre o eixo global: distribuição + transição
+ modal + tensão). A similaridade de retrieval usa união-par-a-par (ok para 1-a-1), mas o clustering
exige o eixo comum. *Consequência:* reuso `_feature_vector`/`_cosine`, não `similarity` diretamente.

**D3 — medoid = maior similaridade média intra-família.** O protótipo é o membro mais "central"
(representa o dialeto). Determinístico; desempate por `song_id`. *Alternativa:* centróide (média dos
vetores) — mas um centróide não é uma música real; medoid é uma peça concreta que o usuário pode ouvir.

**D4 — `k` do usuário, sem "k ótimo".** Cortar o dendrograma em `k` famílias é a operação; `k`
default 8 (musicalmente plausível p/ 293 bossas, mas arbitrário e declarado como tal). Reportar
silhouette/"melhor k" seria transformar descrição em placar — proibido pela lei de ouro.

**D5 — materialização aditiva + CLI descritiva.** `song_cluster` + `v_song_cluster` (derivado/
regenerável). `corpus clusters --k N` mostra, por família: tamanho, protótipo, membros, e os traços
salientes (top funções/cadências agregadas da família) — o "porquê", com denominador visível.

## Risks / Trade-offs

- **[`k` arbitrário lido como verdade]** → Mitigação: a CLI e a spec declaram que `k` é escolha do
  usuário e a família é descritiva; sem "k ótimo", sem placar.
- **[Average-linkage produz uma família gigante + satélites]** → Mitigação: é um fato do dado (a bossa
  tem um núcleo T-SD-D dominante), não um bug; a saída mostra tamanhos (denominador visível). Se
  incomodar, `--linkage` (complete/average) é follow-up trivial.
- **[Vetor dominado por funções frequentes achata famílias]** → Mitigação: a transição (144 dims) traz
  estrutura fina; ponderação TF-IDF é follow-up sem mudar schema.
- **[Regressão nos gates]** → Mitigação: baseline ao vivo antes/depois; a spec exige 293/293 e coder
  intocado (o overlay só LÊ).

## Migration Plan

1. Aditivo: `CREATE TABLE IF NOT EXISTS song_cluster` + `CREATE OR REPLACE VIEW v_song_cluster`.
   Rollback = DROP dos dois; resto do banco intocado.
2. Sem migração de schema base; sem dependência de runtime nova.
3. `corpus clusters` (re)materializa as famílias do run corrente sob demanda para o `k` pedido.

## Open Questions

- **`k` default e critério de corte:** 8 é um chute honesto; expor a hierarquia (permitir vários `k`
  sem recomputar tudo) é follow-up. `--linkage` idem.
- **Traços que "definem" a família:** v1 usa top funções/cadências agregadas; um contraste vs. o
  corpus (o que a família tem A MAIS que a média) seria mais informativo — follow-up.
