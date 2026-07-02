## Why

As análises do motor são **efêmeras**: `analyze_song_data_structured` produz um `result`
dict rico (tom, graus, funções, cadências, escala-acorde, regiões tonais, diagnósticos) que
é despejado num relatório e **descartado**. Não há como perguntar nada sobre a MPB *como
corpus* — distribuição de cadências, progressões recorrentes, vocabulário por tom — nem
auditar os invariantes de qualidade fora do `songbook_baseline.py` em Python imperativo.

Persistir as 170 análises num banco relacional transforma a saída do motor num **corpus
consultável de fatos simbólicos**: dissecar toda a análise (do tom detectado às cadências),
habilitar musicologia de corpus ("medir em vez de achar" em escala), e reexpressar os gates
de qualidade como **views SQL** auditáveis. É a fundação da frente #8 (ampliar/explorar o
corpus) e pré-requisito de qualquer análise de dados futura.

## What Changes

- Novo **schema relacional** (DuckDB) que disseca o `result` dict em 11 tabelas, com grão
  na **ocorrência de acorde** (um acorde numa posição de uma música ≈ 8.500 linhas p/ n=170):
  proveniência (`analysis_run`), dimensões (`function_ref`, `cadence_family_ref`,
  `chord_vocab`), fato (`song`, `chord_occurrence`) e satélites (`chord_scale`, `cadence`,
  `tonal_region`, `modal_coloring`, `diagnostic`).
- **Materializador** que roda o motor sobre o corpus local (`cifras/*.md` via
  `cifra_from_text`, sem rede) e popula o banco — regenerável e versionado por
  `engine_version` + `git_sha` (snapshot: cada materialização é um `analysis_run`).
- **Views de gate** — os 3 invariantes intervalar-simples do baseline (trítono⇒dominante,
  diminuto, coerência cadência×função) reexpressos como consultas declarativas; o ledger de
  corroboração de centro (`agree`/`diverge`/`quarantine`) e um bigrama de função (analytics)
  também como views.
- **Novos comandos CLI** `harmonic corpus build` (materializa) e `harmonic corpus gates`
  (roda as views de gate e falha se houver violação — paridade com o baseline).
- **Invariante inegociável:** o banco guarda a **VERDADE do motor** (derivada, regenerável),
  **nunca** a anotação da fonte (`cc_key`) e **nunca vira ouro** competindo com Chediak. É uma
  *materialized view* do motor + árbitro, não uma nova autoridade.

## Capabilities

### New Capabilities
- `analysis-corpus-persistence`: schema relacional que disseca o `result` do motor,
  materializador a partir do corpus local, proveniência versionada por `analysis_run`, e
  contrato de regenerabilidade (o banco é derivado, nunca fonte de verdade).
- `corpus-query-gates`: views SQL de gate (trítono/diminuto/cadência), ledger de corroboração
  de centro, e views de analytics de corpus (bigrama de função); comandos CLI `corpus build`
  e `corpus gates`.

### Modified Capabilities
<!-- Nenhuma capability existente muda de requisito: o motor e o songbook_baseline.py
     permanecem intactos; a persistência é aditiva e read-only sobre a saída do motor. -->

## Impact

- **Nova dependência:** `duckdb` (analítico/colunar; integra Polars/Parquet). Isolada num
  novo módulo de persistência — o núcleo (`cifra_core`, `harmonic_analysis.domain`) não a
  importa.
- **Onde vive o código:** módulo `harmonic_analysis/persistence/` (schema + materializador +
  views), consumindo `analyze_song_data_structured` e `chediak_functional_center` já
  existentes. Decisão de empacotamento (módulo vs. novo pacote `cifra_corpus`) fica no design.
- **CLI:** novo subcomando `corpus` em `harmonic_analysis/cli/main.py`.
- **Corpus:** lê `cifras/*.md` (gitignored por copyright) — o `.duckdb` gerado também é
  gitignored (artefato derivado, regenerável via `corpus build`).
- **Sem impacto no motor:** zero alteração em detecção/função/cadência; a materialização é um
  consumidor read-only. O `songbook_baseline.py` segue sendo a fonte canônica dos gates; as
  views são uma segunda expressão auditável, verificada por paridade nos testes.
