## MODIFIED Requirements

### Requirement: Agrupamento hierárquico por perfil harmônico

O sistema SHALL agrupar as músicas do run corrente em `k` famílias por agrupamento aglomerativo
sobre a distância de cosseno (1 − similaridade) entre os embeddings harmônicos por música (reusando
`style_fingerprint`), vetorizados num eixo de funções **global** para comparabilidade. O critério de
ligação SHALL ser um parâmetro do usuário: **`average`** (padrão — distância entre famílias = média
das distâncias par-a-par) ou **`complete`** (distância = MÁXIMO par-a-par, favorecendo famílias mais
compactas/equilibradas). O número de famílias `k` SHALL ser um parâmetro do usuário; o sistema NÃO
SHALL alegar um `k` "ótimo" nem um linkage "ótimo" (é descritivo, não placar). O agrupamento SHALL
ser transposição-invariante (features de função) e determinístico para um dado run, `k` e linkage.

#### Scenario: k famílias sobre o run corrente

- **WHEN** o agrupamento roda com um `k` sobre M músicas (k ≤ M)
- **THEN** cada música pertence a exatamente uma família, e há no máximo `k` famílias

#### Scenario: Determinismo

- **WHEN** o agrupamento roda duas vezes sobre o mesmo run, o mesmo `k` e o mesmo linkage
- **THEN** as famílias resultantes (e seus medoids) são idênticas

#### Scenario: Músicas idênticas caem na mesma família

- **WHEN** duas músicas têm o mesmo perfil de função (similaridade 1.0)
- **THEN** elas pertencem à mesma família (em qualquer linkage)

#### Scenario: Complete-linkage produz partição mais equilibrada

- **WHEN** o agrupamento roda com `linkage = complete` no mesmo `k` que `average`
- **THEN** a maior família resultante NÃO é maior que a maior família do `average` (partição não menos equilibrada)
