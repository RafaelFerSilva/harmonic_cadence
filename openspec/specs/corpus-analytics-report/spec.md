# corpus-analytics-report Specification

## Purpose
TBD - created by archiving change corpus-analytics. Update Purpose after archive.
## Requirements
### Requirement: Views de analytics musicológicos sobre o corpus persistido

O sistema SHALL expor, como views SQL sobre o banco do corpus, agregações **descritivas**
cobrindo ao menos: (a) distribuição de cadências por família (contagem de instâncias e de
músicas, juntando a página Chediak da dimensão); (b) trigramas de função
(`function_code[i] → [i+1] → [i+2]`, por frequência); (c) vocabulário por modo detectado
(qualidades de acorde × modo, com contagem); (d) densidade de dominantes
secundários/substitutos (`Dsec`/`Daux`/`Dext`/`SubV`/`Sub2`) por música e média do corpus; e
(e) o **ledger de trítono agrupado por padrão** (função-alvo × grau-base × qualidade, com
contagem, nº de músicas e símbolos-exemplo). As views SHALL ser puramente derivadas das tabelas
de fato — nenhuma re-execução do motor.

#### Scenario: Distribuição de cadências agrega o corpus

- **WHEN** a view de distribuição de cadências é consultada sobre um corpus materializado
- **THEN** ela SHALL retornar, por família de cadência, o total de instâncias e o número de
  músicas distintas em que ocorre, sem re-rodar o motor

#### Scenario: Ledger de trítono vira padrões adjudicáveis

- **WHEN** a view de padrões do ledger é consultada
- **THEN** cada linha SHALL representar um padrão (função-alvo, grau-base, qualidade) com sua
  contagem, número de músicas e até 3 símbolos-exemplo — transformando ocorrências soltas em
  insumo de adjudicação Chediak

#### Scenario: Trigrama de função por frequência

- **WHEN** a view de trigramas é consultada
- **THEN** ela SHALL retornar as sequências de três funções consecutivas (mesma música,
  posições contíguas) ordenáveis por frequência

### Requirement: Comando corpus report gera relatório Markdown descritivo

O sistema SHALL prover a ação `report` no subcomando `corpus` da CLI, que consulta as views de
analytics e grava um relatório **Markdown em PT-BR** com seções fixas (corpus e proveniência,
cadências, progressões, vocabulário por modo, dominantes secundários, worklist de curadoria do
trítono). O relatório SHALL ser descritivo: todo número acompanhado do denominador, nenhuma
métrica apresentada como acurácia/placar do motor. Com banco vazio, o comando SHALL falhar de
forma visível instruindo `corpus build`.

#### Scenario: report gera o arquivo com as seções

- **WHEN** o usuário executa `harmonic corpus report` sobre um banco populado
- **THEN** um arquivo Markdown SHALL ser gravado (caminho configurável via `--out`) contendo as
  seis seções, com os dados vindos exclusivamente das views

#### Scenario: Banco vazio falha visível

- **WHEN** o usuário executa `harmonic corpus report` sobre um banco sem músicas
- **THEN** o comando SHALL imprimir orientação para rodar `harmonic corpus build` e sair com
  código de erro diferente de zero

#### Scenario: Relatório nunca é placar

- **WHEN** o relatório é gerado
- **THEN** a seção do ledger de trítono SHALL ser apresentada como worklist de curadoria
  (adjudicação pendente), e nenhuma seção SHALL comparar detect_key ou funções contra o banco
  como taxa de acerto

