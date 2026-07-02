# analysis-corpus-persistence Specification

## Purpose
TBD - created by archiving change persist-analysis-corpus. Update Purpose after archive.
## Requirements
### Requirement: Schema relacional disseca a análise do motor

O sistema SHALL definir um schema relacional que decompõe o `result` dict de
`analyze_song_data_structured` em tabelas, com o **grão na ocorrência de acorde** (um acorde
numa posição de uma música). O schema SHALL cobrir: proveniência (`analysis_run`), dimensões
(`function_ref`, `cadence_family_ref`, `chord_vocab`), o fato (`song`, `chord_occurrence`) e
os satélites derivados de cada seção do `result` (`chord_scale`, `cadence`, `tonal_region`,
`modal_coloring`, `diagnostic`).

#### Scenario: Ocorrência de acorde é o grão do fato

- **WHEN** uma música com N acordes é materializada
- **THEN** a tabela `chord_occurrence` SHALL conter exatamente N linhas para aquela música,
  cada uma com `position` única em `(song_id, position)`, e cada linha SHALL registrar
  `symbol`, `degree`, `function_code`, `strength` e `roman_numeral` conforme o item
  correspondente de `harmonic_analysis`.

#### Scenario: Toda seção do result tem destino no schema

- **WHEN** o `result` dict de uma análise bem-sucedida é dissecado
- **THEN** cada seção não-nula (`cadences`, `chord_scales`, `tonal_regions`,
  `modal_coloring`, `diagnostics`) SHALL ter suas linhas persistidas na tabela satélite
  correspondente, referenciando `song_id` (e `occ_id` quando o grão é o acorde).

#### Scenario: Referências chave-estrangeira íntegras

- **WHEN** uma linha de `chord_occurrence` referencia um `function_code` e um `symbol`
- **THEN** o `function_code` SHALL existir em `function_ref` e o `symbol` SHALL existir em
  `chord_vocab`; a materialização SHALL falhar de forma visível se uma referência não
  resolver, nunca inserir um órfão em silêncio.

### Requirement: Materialização é derivada, regenerável e versionada

O sistema SHALL popular o banco rodando o motor sobre o corpus local (`cifras/*.md` via
`cifra_from_text`, sem rede). Cada execução SHALL gravar um `analysis_run` com
`engine_version`, `git_sha`, `corpus_version` e `generated_at`, e todas as linhas de `song`
daquela execução SHALL referenciar esse `run_id`. O banco SHALL ser inteiramente reconstruível
a partir do motor + corpus.

#### Scenario: Cada materialização é um snapshot versionado

- **WHEN** `corpus build` é executado
- **THEN** uma nova linha `analysis_run` SHALL ser criada com a versão do motor e o SHA do
  git, e as músicas materializadas SHALL apontar para ela — permitindo comparar duas execuções
  de versões diferentes do motor no mesmo banco.

#### Scenario: Banco é reconstruível do zero

- **WHEN** o arquivo do banco é apagado e `corpus build` roda novamente sobre o mesmo corpus
  e a mesma versão do motor
- **THEN** o conteúdo materializado (fatos por música) SHALL ser equivalente ao anterior,
  provando que o banco é um artefato derivado e não uma fonte de verdade independente.

### Requirement: O banco nunca é ouro competindo com Chediak

O sistema SHALL persistir apenas a **saída do motor** (a verdade derivada do algoritmo +
Chediak). O schema SHALL NOT armazenar a anotação de tom da fonte (`cc_key`) como campo de
verdade, e nenhuma métrica ou consulta SHALL tratar o conteúdo do banco como gabarito de
acurácia contra o qual o motor é medido.

#### Scenario: Anotação da fonte não entra como verdade

- **WHEN** o corpus local é materializado
- **THEN** a tabela `song` SHALL registrar `detected_key`/`detected_mode` (saída de
  `detect_key`) e `center_pc`/`center_mode` (saída de `chediak_functional_center`), e SHALL
  NOT conter uma coluna de tom anotado pela fonte usada como verdade.

#### Scenario: Corroboração de centro é ledger, não placar

- **WHEN** `detect_key` e `chediak_functional_center` são comparados para uma música
- **THEN** o resultado SHALL ser gravado em `song.center_status` como um dos rótulos de
  ledger (`agree` / `diverge` / `quarantine`), como registro de curadoria — nunca como
  "acerto/erro" do detector.

