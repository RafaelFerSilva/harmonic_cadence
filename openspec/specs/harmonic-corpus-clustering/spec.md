# harmonic-corpus-clustering

## Purpose

Agrupamento descritivo do corpus por perfil harmônico. Reusando o embedding de estilo
(`style_fingerprint`) por música, esta capability faz agrupamento hierárquico aglomerativo
(*average-linkage* sobre distância de cosseno num eixo de funções global) para reunir as músicas do
run corrente em `k` famílias, identifica a **música-protótipo (medoid)** de cada família,
materializa o resultado (`song_cluster` + view `v_song_cluster`) e o expõe via
`harmonic corpus clusters [--k N]`. É **transposição-invariante** (features de função), determinística
por run + `k`, e o `k` é escolha do usuário — o sistema **não** alega um `k` "ótimo". A subordinação é
estritamente descritiva: **nunca arbitra** — não reescreve `function_code`, não decide centro tonal,
não toca `songbook_baseline.py`, os 3 gates duros nem o `detect_key`; pertencer a uma família não é
veredito de qualidade ou correção.

## Requirements

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

### Requirement: Música-protótipo (medoid) por família

O sistema SHALL identificar, em cada família, a **música-protótipo** (medoid): aquela de maior
similaridade média com as demais da mesma família. Uma família de uma só música SHALL ter essa
música como protótipo.

#### Scenario: Medoid é o centro da família

- **WHEN** uma família tem ≥ 2 músicas
- **THEN** exatamente uma é marcada como medoid, e é a de maior similaridade média intra-família

### Requirement: Famílias materializadas

O sistema SHALL materializar o resultado na tabela `song_cluster` (`run_id`, `song_id`,
`cluster_id`, `is_medoid`) + uma view `v_song_cluster` com os títulos. A tabela SHALL ser derivada e
regenerável (carimbada por `run_id`); NÃO SHALL alterar tabelas-base nem as views de gate/ledger.

#### Scenario: Regeneração não corrompe o banco

- **WHEN** `song_cluster` é rematerializada
- **THEN** as 11 tabelas-base e as views `v_gate_*`/`v_ledger_*` permanecem inalteradas

### Requirement: Consulta de famílias na CLI

O sistema SHALL expor `harmonic corpus clusters [--k N]` que lista, por família: o tamanho, a
música-protótipo, os membros e os **traços harmônicos salientes por CONTRASTE** que a definem. Um
traço saliente é uma função ou família de cadência **sobre-representada** na família em relação à
média do corpus (lift = participação média na família − participação média no corpus > 0), ordenada
por lift decrescente, com o valor do lift **visível**. Quando uma família não tem nenhum traço acima
da média, o sistema SHALL sinalizar isso explicitamente (ela É o baseline do corpus), em vez de
listar funções comuns. A saída SHALL ser descritiva; NÃO SHALL apresentar as famílias como veredito
de qualidade ou correção — família é uma relação descritiva entre músicas.

#### Scenario: Traços por contraste distinguem a família

- **WHEN** o usuário roda `corpus clusters --k N`
- **THEN** cada família mostra as funções/cadências sobre-representadas em relação ao corpus (lift > 0), com o valor do lift visível

#### Scenario: Família-baseline é sinalizada

- **WHEN** uma família não tem nenhuma função/cadência acima da média do corpus
- **THEN** a saída sinaliza que a família é o baseline do corpus (sem inventar traços distintivos)

#### Scenario: Descritivo, nunca placar

- **WHEN** a saída é gerada
- **THEN** ela NÃO contém vocabulário de placar (acurácia/qualidade da família como verdade)

### Requirement: Subordinação descritiva (não arbitra)

O agrupamento SHALL ser estritamente descritivo. Ele SHALL NOT reescrever `function_code`, SHALL NOT
arbitrar centro tonal, e SHALL NOT alterar o `songbook_baseline.py`, os 3 gates duros nem o
`detect_key`. Pertencer a uma família SHALL NOT ser interpretado como qualidade ou correção.

#### Scenario: Gates e coder intactos

- **WHEN** as famílias são materializadas
- **THEN** `songbook_baseline.py` continua reportando os 3 gates duros 293/293
- **AND** nenhum `function_code`/`degree` do `chord_occurrence` é modificado
