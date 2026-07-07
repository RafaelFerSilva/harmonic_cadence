## ADDED Requirements

### Requirement: Agrupamento hierárquico por perfil harmônico

O sistema SHALL agrupar as músicas do run corrente em `k` famílias por agrupamento aglomerativo
(*average-linkage*) sobre a distância de cosseno (1 − similaridade) entre os embeddings harmônicos
por música (reusando `style_fingerprint`), vetorizados num eixo de funções **global** para
comparabilidade. O número de famílias `k` SHALL ser um parâmetro do usuário; o sistema NÃO SHALL
alegar um `k` "ótimo" (é descritivo, não placar). O agrupamento SHALL ser transposição-invariante
(features de função) e determinístico para um dado run e `k`.

#### Scenario: k famílias sobre o run corrente

- **WHEN** o agrupamento roda com um `k` sobre M músicas (k ≤ M)
- **THEN** cada música pertence a exatamente uma família, e há no máximo `k` famílias

#### Scenario: Determinismo

- **WHEN** o agrupamento roda duas vezes sobre o mesmo run e o mesmo `k`
- **THEN** as famílias resultantes (e seus medoids) são idênticas

#### Scenario: Músicas idênticas caem na mesma família

- **WHEN** duas músicas têm o mesmo perfil de função (similaridade 1.0)
- **THEN** elas pertencem à mesma família

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
música-protótipo, os membros e os **traços harmônicos salientes** que a definem (funções/cadências
dominantes em comum). A saída SHALL ser descritiva; NÃO SHALL apresentar as famílias como veredito
de qualidade ou correção — família é uma relação descritiva entre músicas.

#### Scenario: Lista de famílias com protótipo e traços

- **WHEN** o usuário roda `corpus clusters --k N`
- **THEN** a saída mostra cada família com seu protótipo, tamanho e traços salientes

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
