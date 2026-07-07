# functional-anomaly-overlay Specification

## Purpose
Overlay estatístico (Camada C) que ranqueia as ocorrências de acorde do corpus persistido por
SURPRESA funcional — subordinado ao símbolo (**PRATA**: o ML rankeia, o Chediak adjudica). Treina
um LM de sequência sobre os `function_code`s do coder e materializa uma worklist de curadoria que
prioriza as worklists de trítono/centro já suspeitas por teoria (Trilha B alimenta Trilha A). NUNCA
reescreve rótulo, NUNCA arbitra centro, NUNCA é avaliado por acurácia contra o coder — discordância
é sinal, não erro, o que mata a circularidade de treinar/medir sobre a saída do próprio motor.
## Requirements
### Requirement: Modelo de sequência funcional suavizado

O sistema SHALL treinar um modelo de sequência sobre os `function_code`s do corpus persistido
(grão = ocorrência de acorde, por música, em ordem de `position`), estimando a probabilidade
condicional de cada função dado seu contexto de vizinhança por n-grama com *backoff* suavizado
(Witten-Bell ou Kneser-Ney). O modelo SHALL ser derivado e regenerável a partir de um
`analysis_run` do banco, e SHALL registrar o `run_id`/`engine_version` de origem. O modelo NÃO
SHALL usar nenhuma anotação externa (tom do Cifra Club) como feature — só os rótulos do coder.

#### Scenario: Treino sobre o run corrente

- **WHEN** o overlay é materializado sobre um `analysis_run` com N ocorrências
- **THEN** o modelo estima P(função | contexto) para cada uma das 12 funções presentes
- **AND** massa de probabilidade não-nula é atribuída a contextos não vistos (via backoff/suavização), sem P=0

#### Scenario: Fronteiras de música respeitadas

- **WHEN** a sequência de uma música termina e a próxima começa
- **THEN** o contexto de vizinhança NÃO SHALL cruzar a fronteira entre músicas (cada `song_id` é uma sequência independente)

### Requirement: Escore de surpresa por ocorrência

O sistema SHALL computar, para cada ocorrência de acorde, uma surpresa = −log P(função | contexto)
sob o modelo, em unidades reprodutíveis (bits ou nats declarados). Ocorrências com surpresa mais
alta SHALL ranquear mais alto na worklist. O escore SHALL ser determinístico para um dado run
(mesmo run → mesma ordenação).

#### Scenario: Ocorrência estatisticamente improvável flutua ao topo

- **WHEN** uma ocorrência tem função rara dado seu contexto (ex.: um trigrama observado uma única vez no corpus)
- **THEN** sua surpresa é alta e ela aparece no topo da worklist ranqueada

#### Scenario: Determinismo

- **WHEN** o overlay é materializado duas vezes sobre o mesmo `analysis_run`
- **THEN** os escores de surpresa e a ordenação da worklist são idênticos

### Requirement: Worklist materializada e cruzada com os ledgers

O sistema SHALL materializar a worklist como a view `v_anomaly_worklist` no DuckDB, contendo ao
menos `song_id`, `position`, `symbol`, `function_code` e o escore de surpresa. A view SHALL
marcar quais ocorrências também constam em `v_ledger_tritone_nondominant` e/ou em uma música com
centro `diverge` no `v_center_ledger`, para que a surpresa **priorize** as worklists de curadoria
já existentes. A view SHALL ser derivada e regenerável; NÃO SHALL alterar tabelas-base nem as
views de gate/ledger existentes.

#### Scenario: Interseção com o ledger de trítono é sinalizada

- **WHEN** uma ocorrência do `v_ledger_tritone_nondominant` também é surpreendente
- **THEN** ela aparece em `v_anomaly_worklist` com a marca de interseção de trítono, ranqueada pela surpresa

#### Scenario: Regeneração não corrompe o banco

- **WHEN** `v_anomaly_worklist` é remateralizada
- **THEN** as 11 tabelas-base e as views `v_gate_*`/`v_ledger_*` permanecem inalteradas

### Requirement: Relatório de anomalias sem placar

O sistema SHALL expor o subcomando `harmonic corpus anomalies` que emite um relatório Markdown em
PT-BR a partir de `v_anomaly_worklist`. O relatório SHALL exibir **denominadores visíveis** (total
de ocorrências, quantas na worklist, cobertura) e SHALL NOT apresentar qualquer métrica como
placar de acurácia/qualidade do detector — o overlay é descritivo e a decisão é do Chediak. O
relatório SHALL declarar explicitamente que o ML **rankeia** e o Chediak **adjudica**.

#### Scenario: Relatório mostra denominador, não placar

- **WHEN** o usuário roda `harmonic corpus anomalies`
- **THEN** o relatório lista as ocorrências mais surpreendentes com seus denominadores
- **AND** NÃO contém nenhuma linha do tipo "acurácia/precisão do modelo = X%" ou placar equivalente

#### Scenario: Guarda-corpo anti-placar testado

- **WHEN** a suíte de testes verifica o texto do relatório
- **THEN** um teste falha se aparecer vocabulário de placar (acurácia/precisão/score do modelo como verdade)

### Requirement: Subordinação ao símbolo (PRATA, nunca ouro)

O overlay SHALL ser estritamente subordinado ao motor simbólico. Ele SHALL NOT reescrever
`function_code`, SHALL NOT arbitrar centro tonal, e SHALL NOT alterar o resultado do
`songbook_baseline.py`, dos 3 gates duros (diminuto/D2/cadência) nem do `detect_key`. A saída do
overlay SHALL ser consumida apenas como worklist de curadoria (sinal), nunca como verdade.

#### Scenario: Gates duros e baseline intactos

- **WHEN** o overlay é adicionado e materializado
- **THEN** `songbook_baseline.py` continua reportando os 3 gates duros 293/293
- **AND** nenhum `function_code` no `chord_occurrence` é modificado pelo overlay
