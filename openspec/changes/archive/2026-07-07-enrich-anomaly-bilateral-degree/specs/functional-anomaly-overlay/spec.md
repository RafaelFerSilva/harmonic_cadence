## MODIFIED Requirements

### Requirement: Modelo de sequência funcional suavizado

O sistema SHALL treinar modelos de sequência sobre o corpus persistido (grão = ocorrência de
acorde, por música, em ordem de `position`), estimando a probabilidade condicional de cada token
dado seu contexto de vizinhança por n-grama com *backoff* suavizado (Witten-Bell ou Kneser-Ney).
O sistema SHALL treinar em **duas direções** (causal esquerda→direita e reversa direita→esquerda)
e em **dois canais**: `function_code` e `degree` (grau em algarismo romano; `NULL` mapeado ao
token sentinela `∅`). Todos os modelos SHALL ser derivados e regeneráveis de um `analysis_run`,
SHALL registrar o `run_id`/`engine_version` de origem, e NÃO SHALL usar anotação externa (tom do
Cifra Club) como feature — só os rótulos do coder.

#### Scenario: Treino sobre o run corrente

- **WHEN** o overlay é materializado sobre um `analysis_run` com N ocorrências
- **THEN** os modelos estimam P(token | contexto) para os tokens de função e de grau presentes
- **AND** massa de probabilidade não-nula é atribuída a contextos não vistos (via backoff/suavização), sem P=0

#### Scenario: Fronteiras de música respeitadas nas duas direções

- **WHEN** a sequência de uma música termina e a próxima começa
- **THEN** nem o contexto causal nem o reverso SHALL cruzar a fronteira entre músicas (cada `song_id` é uma sequência independente em ambas as direções)

### Requirement: Escore de surpresa por ocorrência

O sistema SHALL computar, para cada ocorrência de acorde, uma surpresa em bits (unidade declarada)
combinando as duas direções e os dois canais. A surpresa de um canal SHALL ser a **média** das
surpresas causal e reversa (−log₂ P nos dois sentidos); o escore combinado `surprise_bits` SHALL
ser a **média** da surpresa de função e da surpresa de grau. Os componentes por canal
(`surprise_function`, `surprise_degree`) SHALL ficar visíveis (não caixa-preta). Ocorrências com
`surprise_bits` mais alto SHALL ranquear mais alto na worklist. O escore SHALL ser determinístico
para um dado run.

#### Scenario: Ocorrência anômala nos dois sentidos flutua ao topo

- **WHEN** uma ocorrência é rara tanto dado o passado quanto dado o futuro (contexto bilateral)
- **THEN** sua surpresa combinada é alta e ela aparece no topo da worklist ranqueada

#### Scenario: Componentes de função e grau são reportados

- **WHEN** uma ocorrência é pontuada
- **THEN** `surprise_function` e `surprise_degree` estão disponíveis ao lado de `surprise_bits`

#### Scenario: Determinismo

- **WHEN** o overlay é materializado duas vezes sobre o mesmo `analysis_run`
- **THEN** os escores e a ordenação da worklist são idênticos

### Requirement: Worklist materializada e cruzada com os ledgers

O sistema SHALL materializar a worklist como a view `v_anomaly_worklist` no DuckDB, contendo ao
menos `song_id`, `position`, `symbol`, `function_code`, `degree`, o escore combinado
`surprise_bits` e os componentes `surprise_function`/`surprise_degree`. A view SHALL marcar quais
ocorrências também constam em `v_ledger_tritone_nondominant` e/ou em uma música com centro
`diverge` no `v_center_ledger`, para que a surpresa **priorize** as worklists de curadoria já
existentes. A view SHALL ser derivada e regenerável; NÃO SHALL alterar tabelas-base nem as views
de gate/ledger existentes.

#### Scenario: Interseção com o ledger de trítono é sinalizada

- **WHEN** uma ocorrência do `v_ledger_tritone_nondominant` também é surpreendente
- **THEN** ela aparece em `v_anomaly_worklist` com a marca de interseção de trítono, ranqueada pela surpresa combinada

#### Scenario: Regeneração não corrompe o banco

- **WHEN** `v_anomaly_worklist` é remateralizada
- **THEN** as 11 tabelas-base e as views `v_gate_*`/`v_ledger_*` permanecem inalteradas
