## Why

A camada simbólica do motor está madura (Chediak Vol. I destilado até o Cap. XXXIV,
3 gates duros 293/293) e a ingestão de dados foi encerrada (n=293 congelado). O norte
virou **desenvolver e analisar o que temos**. Restam duas worklists honestas de curadoria
— o ledger de trítono (43 ocorrências em 20 músicas) e a worklist de centro (46 divergências)
— que hoje são adjudicadas contra o Chediak **sem priorização**: não há sinal de *onde* olhar
primeiro. Ao mesmo tempo, o corpus já está materializado no DuckDB no grão de ocorrência de
acorde, um dataset PRATA pronto para um overlay estatístico. Esta é a **primeira change da
Camada C** (overlay ML/NLP): usar a estatística do próprio corpus para **ranquear** o que
adjudicar, unindo Trilha B (mecanismo) a Trilha A (adjudicação) numa frente só.

## What Changes

- Novo overlay estatístico **descritivo** sobre `corpus.duckdb`: um LM de sequência funcional
  com *backoff* suavizado (Witten-Bell/Kneser-Ney) treinado nos 12 `function_code`s rotulados
  pelo coder (`T`, `SD`, `D`, `Emp`, `Dsec`, `D2`, `Dext`, `Dim`, `SubV`, `Daux`, `Crom`,
  `Outro`).
- Métrica de **surpresa por ocorrência** = −log P(função | contexto de vizinhança), materializada
  como worklist ranqueada e cruzada com `v_ledger_tritone_nondominant` e `v_center_ledger`.
- Nova view `v_anomaly_worklist` no banco + subcomando CLI `harmonic corpus anomalies` que emite
  relatório Markdown PT-BR com **denominador visível, nunca placar** (mesmo guarda-corpo testado
  do `corpus report`).
- **Lei de ferro (não-negociável):** o overlay é **PRATA** — o ML **rankeia**, o Chediak
  **adjudica**. Ele NUNCA reescreve `function_code`, NUNCA arbitra centro, NUNCA compete com o
  ouro. Discordância entre a estatística e o rótulo do coder é **sinal de curadoria**, não erro
  — é isso que mata a circularidade de treinar/avaliar contra o próprio coder.
- Overlay é **derivado e regenerável** (como o resto do banco): re-materializável por
  `engine_version`/`git_sha`; treino sobre o run corrente.

## Capabilities

### New Capabilities
- `functional-anomaly-overlay`: modelo de sequência funcional (n-grama suavizado) sobre o corpus
  persistido, escore de surpresa por ocorrência, worklist ranqueada materializada como view SQL,
  cruzamento com os ledgers existentes (trítono/centro), e relatório CLI PT-BR com denominador
  visível. Explicitamente subordinado ao símbolo (PRATA, nunca ouro).

### Modified Capabilities
<!-- Nenhuma capability existente muda de REQUISITO. O overlay LÊ o banco derivado (grão de
     ocorrência) e as views de ledger, sem alterar o contrato do motor, dos 3 gates duros, do
     detect_key, nem da persistência. -->

## Impact

- **Novo código:** subpacote `harmonic_analysis/overlay/` (modelo + materialização + relatório);
  subcomando `harmonic corpus anomalies` em `cli/main.py`; testes em
  `packages/harmonic_analysis/tests/`.
- **Banco:** adiciona a view `v_anomaly_worklist` (derivada; regenerável). Não altera as 11
  tabelas-base nem as views de gate/ledger existentes.
- **Dependências:** preferir SQL puro / stdlib (`math`, contagem de n-gramas em DuckDB) para o
  n-grama suavizado — sem dependência ML pesada nesta primeira change (símbolo domina, ML mínimo
  e interpretável sobre 12 tokens).
- **Não toca:** os 3 gates duros (diminuto/D2/cadência, 293/293), o `detect_key`, o
  `songbook_baseline.py` (que segue sendo a régua ao vivo — a change mede contra ele).
- **Copyright:** relatório e banco seguem gitignored (só FATOS/mecanismo entram no repo).
