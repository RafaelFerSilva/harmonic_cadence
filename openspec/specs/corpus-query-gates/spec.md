# corpus-query-gates Specification

## Purpose
TBD - created by archiving change persist-analysis-corpus. Update Purpose after archive.
## Requirements
### Requirement: Gates executáveis expressos como views SQL

O sistema SHALL expor como views SQL os invariantes de qualidade que são **verdadeiros
invariantes** no corpus (sem exceção documentada), de modo que a view retorne exatamente as
linhas em **violação** (view vazia = gate verde) e o comando `corpus gates` **falhe** em
qualquer violação. SHALL cobrir ao menos: (a) diminuto ⇒ apenas `D`/`Dsec`/`Dim` (Chediak
XXI-XXII); (b) coerência cadência×função (cadência resolutiva com alvo não-repouso, Chediak
XXXII); (c) resolução do `D2` (Chediak XIX). O gate intervalar de múltiplos acordes (`D2`) SHALL
ser re-derivado no motor e persistido como coluna (`d2_resolved`), consultável por view trivial.

#### Scenario: View de gate executável retorna só violações

- **WHEN** a view `v_gate_diminished` é consultada sobre um corpus sem defeito
- **THEN** ela SHALL retornar zero linhas; e SHALL retornar uma linha por ocorrência em
  violação (`song_id`, `position`, `symbol`, `function_code`).

#### Scenario: Paridade com os caminhos EXECUTÁVEIS do baseline

- **WHEN** as views de gate executáveis rodam sobre o mesmo corpus que `songbook_baseline.py`
- **THEN** o conjunto de violações SHALL ser idêntico ao do baseline **apenas para os
  invariantes que o baseline de fato executa** (diminuto, D2, cadência×função). A paridade
  SHALL NOT ser afirmada contra gates que o baseline não executa (ver o ledger de trítono).

### Requirement: Trítono não-dominante é ledger de curadoria, não gate

O sistema SHALL tratar a leitura trítono-real-não-dominante como ledger de curadoria, não como
gate que falha o build. O invariante "todo trítono real ⇒ função dominante" **não é** um
invariante limpo no corpus:
o motor lê legitimamente muitos acordes de trítono real como `T` (tônica `I7` de blues/funk,
cf. `i7-funk-anchor`) ou `Emp` (empréstimo modal). Portanto o sistema SHALL expor a leitura
trítono-real-não-dominante como um **ledger de curadoria** (worklist a adjudicar por Chediak),
**não** como gate que falha o build. O comando `corpus gates` SHALL reportar a contagem do
ledger de forma informativa, sem sair com erro por causa dele. A view
`v_ledger_tritone_nondominant` SHALL, além de identificar cada ocorrência, expor o **veredito
adjudicado** e a **página Chediak citada** quando a ocorrência já foi adjudicada (via corpus
`tritone-adjudication`), mantendo-se informativa e aditiva (rollback = reverter a view).

#### Scenario: Ledger de trítono é informativo, não bloqueante

- **WHEN** `corpus gates` roda sobre o corpus atual (que contém acordes de trítono real lidos
  como `T`/`Emp`)
- **THEN** o comando SHALL imprimir a contagem de ocorrências trítono-real-não-dominante como
  worklist de curadoria, e SHALL NOT sair com erro por causa dessas ocorrências (só os gates
  executáveis bloqueiam).

#### Scenario: Ledger identifica cada ocorrência e seu veredito

- **WHEN** a view `v_ledger_tritone_nondominant` é consultada
- **THEN** ela SHALL retornar, por ocorrência de trítono real cujo `function_code` não é
  dominante, o `song_id`, `position`, `symbol` e `function_code` — insumo de adjudicação, nunca
  placar de acerto/erro — E, quando a ocorrência já foi adjudicada, o `verdict` e a página
  Chediak citada; ocorrência ainda não adjudicada SHALL aparecer com veredito nulo (não some da
  view).

### Requirement: Analytics de corpus como views

O sistema SHALL expor consultas de análise de corpus como views, incluindo ao menos o
**ledger de corroboração de centro** (contagem por `center_status`) e o **bigrama de função**
(frequência de transições `function_code[i] → function_code[i+1]` sobre todas as músicas).

#### Scenario: Bigrama de função agrega o corpus inteiro

- **WHEN** a view `v_function_bigram` é consultada
- **THEN** ela SHALL retornar, por par de funções consecutivas, a contagem de ocorrências em
  todo o corpus, ordenável por frequência — sem re-rodar o motor.

#### Scenario: Ledger de centro resume a corroboração

- **WHEN** a view `v_center_ledger` é consultada
- **THEN** ela SHALL retornar a contagem de músicas por `center_status`
  (`agree`/`diverge`/`quarantine`).

### Requirement: Comandos CLI de corpus

O sistema SHALL prover um subcomando `corpus` na CLI `harmonic` com ao menos:
`corpus build` (materializa o corpus local no banco) e `corpus gates` (roda as views de gate
e sai com código de erro se houver qualquer violação).

#### Scenario: build materializa o corpus local

- **WHEN** o usuário executa `harmonic corpus build`
- **THEN** o motor SHALL rodar sobre `cifras/*.md` sem acesso à rede e o banco SHALL ser
  populado com um novo `analysis_run` e as músicas correspondentes.

#### Scenario: gates falha só em violação de gate executável

- **WHEN** o usuário executa `harmonic corpus gates` sobre um corpus com ao menos uma
  violação de gate **executável** (diminuto, D2 ou cadência×função)
- **THEN** o comando SHALL listar as violações e sair com código diferente de zero; com corpus
  limpo nesses gates, SHALL sair com código zero — independentemente da contagem do ledger de
  trítono (que é informativo).

