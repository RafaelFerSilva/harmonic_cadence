## 1. Fundação e dependência

- [x] 1.1 Adicionar `duckdb` como dependência do pacote `harmonic_analysis` (isolada; núcleo não importa)
- [x] 1.2 Criar o módulo `harmonic_analysis/persistence/` com `db.py` (abre/cria conexão DuckDB, import tardio)
- [x] 1.3 Ignorar o artefato do banco (`*.duckdb`) no `.gitignore`

## 2. Schema

- [x] 2.1 Escrever `persistence/schema.sql` com as 11 tabelas (dialeto portável SQLite/DuckDB): `analysis_run`, `function_ref`, `cadence_family_ref`, `chord_vocab`, `song`, `chord_occurrence`, `chord_scale`, `cadence`, `tonal_region`, `modal_coloring`, `diagnostic`
- [x] 2.2 Definir chaves e FKs conforme o design (grão `(song_id, position)` único; FKs `function_code`→`function_ref`, `symbol`→`chord_vocab`)
- [x] 2.3 Seed estático de `function_ref` (14 códigos de `harmony.py` + label PT + `is_repose` + página Chediak) e `cadence_family_ref` (7 famílias de `cadence.py` + `is_resolving`)
- [x] 2.4 Teste: aplicar o schema numa DB temporária e verificar tabelas/seeds criados

## 3. Materializador (motor → linhas)

- [x] 3.1 `persistence/materialize.py`: enumerar `cifras/*.md`, ingerir via `cifra_from_text` e rodar `analyze_song_data_structured` (sem rede) — reusa o caminho do `songbook_baseline.py`
- [x] 3.2 Criar `analysis_run` (engine_version, git_sha, corpus_version, generated_at) e inserir `song` referenciando o run (incl. `detected_key/mode`, `center_pc/mode`, `center_status`, `n_chords`)
- [x] 3.3 Computar `center_status` (`agree`/`diverge`/`quarantine`) via `detect_key` × `chediak_functional_center` (reusar a lógica do baseline)
- [x] 3.4 Popular `chord_vocab` (upsert por `symbol`: root_pc, spelling, bass_pc, quality, category, slots, tensions JSON, `has_real_tritone`) a partir do parse existente
- [x] 3.5 Popular `chord_occurrence` (grão): position, symbol, degree, function_code, strength, roman_numeral, `is_subv_chain`, `is_ii_cadential`, `d2_resolved` (reusa `_d2_resolution_invariant`)
- [x] 3.6 Popular satélites: `chord_scale` (só diatônicos), `tonal_region`, `modal_coloring`, `diagnostic`
- [x] 3.7 Reconstruir posições da cadência (D5): re-caminhar `degree_seq`/`symbols` para `from/to_position`, `is_modulating`, `suppressed`; inserir em `cadence`
- [x] 3.8 Degradação visível: música que falha na materialização é logada e registrada, não engolida
- [x] 3.9 Teste: materializar um mini-corpus fixture e conferir contagem de linhas por tabela e integridade de FK

## 4. Views (gates + ledger + analytics)

- [x] 4.1 `persistence/views.sql`: gates EXECUTÁVEIS `v_gate_diminished`, `v_gate_cadence` (retornam só violações)
- [x] 4.2 View de gate `D2` (`v_gate_d2`) sobre a coluna `d2_resolved` persistida
- [x] 4.3 View LEDGER `v_ledger_tritone_nondominant` (trítono real lido como não-dominante — worklist, NÃO gate; ver D9)
- [x] 4.4 Views de analytics: `v_center_ledger` (contagem por `center_status`) e `v_function_bigram`
- [x] 4.5 Teste de paridade (D8): as views de gate EXECUTÁVEIS (diminuto, D2, cadência) produzem o MESMO conjunto de violações que os caminhos executáveis do `songbook_baseline.py` — NÃO afirmar paridade de trítono (baseline é no-op)

## 5. CLI

- [x] 5.1 Adicionar subcomando `corpus` em `cli/main.py` com `build` e `gates` (import tardio de `persistence`)
- [x] 5.2 `corpus build`: materializa o corpus local, imprime resumo (run_id, n_songs, ledger de centro)
- [x] 5.3 `corpus gates`: roda os gates EXECUTÁVEIS (diminuto/D2/cadência) — violação → lista e exit ≠ 0; imprime a contagem do ledger de trítono de forma informativa (não bloqueia)
- [x] 5.4 Teste: `corpus build` seguido de `corpus gates` num fixture retorna verde (exit 0) nos gates executáveis

## 6. Fechamento

- [x] 6.1 `make test` e `make lint` verdes
- [x] 6.2 Nota no AGENTS.md / ROADMAP sobre a camada de persistência (aditiva; banco = view materializada do motor, nunca ouro)
- [ ] 6.3 `openspec archive persist-analysis-corpus`
