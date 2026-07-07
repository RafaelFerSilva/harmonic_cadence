## ADDED Requirements

### Requirement: Embedding harmônico por música

O sistema SHALL construir, para cada música do run corrente, um vetor de features harmônicas
(reusando o `Fingerprint` de `style_fingerprint`) a partir do corpus persistido: distribuição de
função, matriz de transição função→função, contagem de cadências, uso modal e densidade de tensão.
O embedding SHALL ser **transposição-invariante** (baseado em função, não em tom) e derivado só do
corpus persistido — NÃO SHALL usar anotação externa (tom do Cifra Club) como feature.

#### Scenario: Um vetor por música do run corrente

- **WHEN** o embedding é construído sobre um `analysis_run` com M músicas
- **THEN** existe exatamente um `Fingerprint` por música (grão de música, `song_count = 1`)

#### Scenario: Invariância a transposição

- **WHEN** duas músicas têm a MESMA sequência de funções em tons diferentes
- **THEN** seus embeddings são iguais (a similaridade entre elas é 1.0)

### Requirement: Similaridade e vizinhos materializados

O sistema SHALL computar a similaridade de cosseno (reusando `style_fingerprint.similarity`) entre
os embeddings e materializar os **top-K vizinhos** de cada música numa tabela `song_neighbor`
(`run_id`, `song_id`, `neighbor_id`, `rank`, `similarity`) + uma view `v_song_neighbor` com os
títulos. A tabela SHALL ser derivada e regenerável (carimbada por `run_id`); NÃO SHALL alterar
tabelas-base nem as views de gate/ledger. A similaridade SHALL ficar em [0, 1] e a ordenação por
`rank` SHALL refletir similaridade decrescente. Uma música NÃO SHALL ser vizinha de si mesma.

#### Scenario: Top-K vizinhos por música

- **WHEN** os vizinhos são materializados com K
- **THEN** cada música tem no máximo K vizinhos, ordenados por similaridade decrescente, sem incluir a si mesma

#### Scenario: Regeneração não corrompe o banco

- **WHEN** `song_neighbor` é rematerializada
- **THEN** as 11 tabelas-base e as views `v_gate_*`/`v_ledger_*` permanecem inalteradas

#### Scenario: Determinismo

- **WHEN** os vizinhos são materializados duas vezes sobre o mesmo `analysis_run`
- **THEN** a tabela `song_neighbor` e a ordenação são idênticas

### Requirement: Consulta de similaridade na CLI

O sistema SHALL expor `harmonic corpus similar --song <slug> [--k N]` que resolve o slug para a
música e lista seus vizinhos mais próximos com a similaridade e os **traços harmônicos
compartilhados** (funções/cadências salientes em comum) — o "porquê" da proximidade, não um número
solto. A saída SHALL ser descritiva; NÃO SHALL apresentar a similaridade como veredito de qualidade
ou correção. Um slug inexistente SHALL falhar de forma visível (mensagem clara), nunca em silêncio.

#### Scenario: Lista de vizinhos com traços compartilhados

- **WHEN** o usuário roda `corpus similar --song <slug>`
- **THEN** a saída lista as músicas mais próximas, cada uma com a similaridade e os traços em comum

#### Scenario: Slug inexistente falha visível

- **WHEN** o slug informado não existe no corpus
- **THEN** o comando emite uma mensagem de erro clara e não retorna vizinhos silenciosamente

### Requirement: Subordinação descritiva (não arbitra)

O overlay de similaridade SHALL ser estritamente descritivo. Ele SHALL NOT reescrever
`function_code`, SHALL NOT arbitrar centro tonal, e SHALL NOT alterar o `songbook_baseline.py`, os
3 gates duros nem o `detect_key`. Similaridade SHALL NOT ser interpretada como medida de qualidade
ou correção — é uma relação descritiva entre músicas.

#### Scenario: Gates e coder intactos

- **WHEN** os embeddings e vizinhos são materializados
- **THEN** `songbook_baseline.py` continua reportando os 3 gates duros 293/293
- **AND** nenhum `function_code`/`degree` do `chord_occurrence` é modificado
