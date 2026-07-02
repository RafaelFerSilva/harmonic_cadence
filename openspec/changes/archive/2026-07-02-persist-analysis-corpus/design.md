## Context

O motor (`AnalysisService.analyze_song_data_structured`) já emite um `result` dict rico e
estável, e o `songbook_baseline.py` já roda o motor sobre o corpus local (`cifras/*.md` via
`cifra_from_text`, sem rede) para validar invariantes. O que falta é **persistir** essa saída:
hoje ela é calculada e descartada. Esta change adiciona uma camada de persistência **read-only
sobre a saída do motor** — sem tocar detecção/função/cadência.

Restrições herdadas do projeto (inegociáveis):
- **Fonte vs. verdade:** o banco guarda a saída do motor (verdade derivada), nunca o `cc_key`.
- **Uma fonte por preocupação:** reusar `analyze_song_data_structured` e
  `chediak_functional_center`; não reimplementar detecção/função na camada de persistência.
- **Degradação visível:** materialização que falha numa música reporta (não engole).
- O `songbook_baseline.py` permanece a **fonte canônica** dos gates; as views são segunda
  expressão, verificada por paridade.

Forma real das seções do `result` (levantada em explore, ancorada no código):
`harmonic_analysis[]` = `{chord, degree, quality, strength, function_code, function,
function_description}`; `cadences` = `{família: set("A → B")}` (7 famílias, **sem índice**);
`chord_scales[]` = `{chord, scale, tensions[], avoid[]}`; `tonal_regions[]` =
`{start, end, key, score}`; `modal_coloring` = `{flavor, evidence[], where[]}`;
`diagnostics[]` = `{section, error}`.

## Goals / Non-Goals

**Goals:**
- Dissecar o `result` num schema relacional com grão na ocorrência de acorde (11 tabelas).
- Materializador regenerável e versionado (`analysis_run` = snapshot por versão de motor).
- Gates e analytics como views SQL; comandos `corpus build` / `corpus gates`.
- Paridade verificável entre as views de gate e o `songbook_baseline.py`.

**Non-Goals:**
- Nenhuma mudança no motor, na detecção, nas funções ou nas cadências.
- Nenhum ML/NLP (é a Change B, dependente desta).
- Nenhuma ingestão via rede (materializa só o corpus local).
- Não substituir o `songbook_baseline.py` — ele segue canônico; as views o espelham.

## Decisions

### D1 — Engine: DuckDB (não SQLite)
O workload é analítico (group-by/n-gram sobre a tabela de fato), não transacional. DuckDB é
colunar, integra Polars/Parquet nativamente (habilita a Change B), e o schema é portável.
Isolado num módulo de persistência; o núcleo não importa `duckdb`.
*Alternativa:* SQLite (já é o dialeto do `JsonFileCacheStore`) — rejeitado por ser fraco em
OLAP e não pavimentar a camada de analytics. O DDL é escrito em subconjunto portável.

### D2 — Grão = ocorrência de acorde; fato = `chord_occurrence`
Star schema. Dimensões song-independent (`chord_vocab`, `function_ref`, `cadence_family_ref`)
são compartilhadas; `song` é o cabeçalho; satélites (`chord_scale`, `cadence`, …) penduram no
`song_id`/`occ_id`. ~8.500 linhas de fato p/ n=170 — trivial em volume, ótimo p/ agregação.

### D3 — Snapshot versionado (`analysis_run`), não single-current
Cada `corpus build` cria um `analysis_run` (engine_version + git_sha + corpus_version); as
músicas referenciam o run. Barato (n=170) e permite A/B entre versões do motor ("meu novo gate
quebrou algo?"). *Alternativa:* sobrescrever o corrente — rejeitado (perde a capacidade de
comparação, que é metade do valor).

### D4 — Gate `D2` materializado no motor, não view SQL
Os gates trítono/diminuto/cadência são intervalar-simples → views legíveis. O gate `D2 resolve
no alvo` precisa de `i, i+1, i+2` intervalar; em SQL vira self-join triplo ilegível. Decisão:
reusar `_d2_resolution_invariant` no materializador e persistir o resultado como coluna
(`chord_occurrence.is_ii_cadential` + `d2_resolved`), consultável por view trivial.

### D5 — Reconstruir posição da cadência na materialização
A saída atual de `analyze_cadences` é um `set` de strings `"A → B"` **sem índice**. O
materializador re-caminha `degree_seq`/`symbols` (a mesma lógica de `cadence.py`) para
recuperar `from_position`/`to_position` e os flags `is_modulating`/`suppressed`. Custo O(n),
sem alterar o motor.

### D6 — Onde vive o código: `harmonic_analysis/persistence/`
Módulo novo dentro do pacote existente (não um pacote `cifra_corpus` separado), porque ele
consome tipos de domínio (`analyze_song_data_structured`, `chediak_functional_center`) e não é
reusado por `cifra_core`/`cifra_scraper`. Estrutura: `schema.sql` (DDL), `materialize.py`
(motor → linhas), `views.sql` (gates + analytics), `db.py` (conexão DuckDB).
*Alternativa:* novo pacote no workspace — rejeitado por acoplamento a domínio; reavaliar se a
Change B pedir reuso.

### D7 — Listas como JSON text
`tensions`/`avoid`/`evidence`/`where` viram colunas JSON text (portável SQLite/DuckDB) em vez
de `LIST`/`STRUCT` nativos do DuckDB, para manter o DDL agnóstico e legível.

### D8 — Paridade como teste, mas só contra caminhos EXECUTÁVEIS do baseline
Um teste roda `songbook_baseline.py` e as views de gate sobre o mesmo corpus e afirma conjuntos
idênticos — porém **apenas para os gates que o baseline realmente executa** (diminuto, D2,
cadência×função). Ver D9: os gates de trítono/diminuto do baseline chamam um método inexistente
e são no-ops; o de diminuto casualmente coincide (0 violações), então a paridade vale; o de
trítono não tem oráculo válido e é tratado como ledger (D9).

### D9 — Descoberta: 2 gates do baseline são no-ops; trítono vira ledger, não gate
Durante a implementação descobriu-se que `Chord.get_category()` e `Chord.bass` **não existem**;
`_dominant_invariant`/`_diminished_invariant` do `songbook_baseline.py` chamam-nos dentro de
`try/except: continue`, então **não executam** (o "170/170 verde" do trítono/diminuto é
vacuoso). Rodando a checagem correta (`.quality`): **diminuto = 0** (invariante real, vira gate
executável), mas **trítono = 944 flags em 155/170 músicas**, dominadas por `→T` (592; tônica
`I7` de blues/funk, legitimada pelo `i7-funk-anchor`) e `→Emp` (278; empréstimo modal). Logo o
invariante "trítono ⇒ dominante" **não é limpo** — tem exceções que o próprio projeto
introduziu, pendentes de adjudicação Chediak. Decisão: nesta change, trítono-real-não-dominante
é um **ledger de curadoria** (view `v_ledger_tritone_nondominant`, informativo em `corpus
gates`), **não** um gate que falha o build. O bug do baseline + a adjudicação das 944 exceções
viram uma **change separada** (`fix-baseline-noop-gates` / adjudicação de trítono). Assim a
persistência permanece honesta e mínima, e passa a ser a **primeira execução real** desses
checks.

## Risks / Trade-offs

- **[Banco vira "ouro" acidental]** → mitigar por spec (`analysis-corpus-persistence`) +
  ausência de coluna de `cc_key`-verdade + `center_status` como ledger; revisão trata qualquer
  consulta que compare o motor contra o banco como acurácia como bug.
- **[Divergência view × baseline]** → teste de paridade (D8) trava a change; baseline canônico.
- **[Schema drift do `result`]** → o materializador lê chaves nomeadas e falha visível em
  seção ausente inesperada; um teste de contrato fixa a forma esperada das seções.
- **[Nova dependência `duckdb`]** → isolada no módulo de persistência; núcleo e CLI base não a
  importam (import tardio no subcomando `corpus`, como o LLM em `explain/`).
- **[Corpus gitignored → não reprodutível por terceiros]** → aceito (copyright); o `.duckdb` é
  derivado e gitignored, regenerável por quem tiver o corpus.

## Migration Plan

Aditivo, sem migração de dados existentes (não há banco hoje). Rollback = remover o módulo
`persistence/`, o subcomando `corpus` e a dependência `duckdb`; o motor e o baseline ficam
intactos. O `.duckdb` é descartável (regenerável).

## Open Questions

- O `analysis_run` deve reter histórico ilimitado ou podar runs antigos? (Proposta: manter;
  n é pequeno. Revisar se crescer.)
- `chord_vocab` é global (compartilhado entre runs) ou por-run? (Proposta: global, keyed por
  `symbol` — o parse é determinístico e independente de música/versão do motor de detecção.)
- Precisamos persistir `analysis_progression` e `function_stats` (derivados agregáveis por
  view a partir de `chord_occurrence`)? (Proposta: não persistir; derivar por view — evita
  duplicar verdade.)
- `voice_leading` e os numerais romanos completos entram já ou ficam p/ iteração? (Proposta:
  `roman_numeral` entra em `chord_occurrence`; `voice_leading` fica fora do MVP.)
