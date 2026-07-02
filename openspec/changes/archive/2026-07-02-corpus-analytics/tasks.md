## 1. Views de analytics

- [x] 1.1 `v_cadence_distribution`: por família — instâncias, músicas distintas, página Chediak (join `cadence_family_ref`)
- [x] 1.2 `v_function_trigram`: dupla auto-junção por posição (mesma música), contagem por sequência de 3 funções
- [x] 1.3 `v_vocab_by_mode`: qualidade (`chord_vocab.quality`) × modo detectado (`song.detected_mode`), contagem
- [x] 1.4 `v_secondary_density`: % de `Dsec/Daux/Dext/SubV/Sub2` sobre `n_chords` por música + média do corpus
- [x] 1.5 `v_tritone_ledger_patterns`: ledger agrupado por (função-alvo, grau-base normalizado, qualidade) com contagem, nº músicas, `MIN(symbol)` exemplo
- [x] 1.6 Teste: views retornam formas esperadas num fixture; normalização de grau-base cobre os sufixos presentes (`°`, minúsculas, inversão)

## 2. Relatório

- [x] 2.1 `persistence/report.py`: `render_report(conn, top_n=...) -> str` — 6 seções em PT-BR, denominadores visíveis, linguagem descritiva (worklist, não placar)
- [x] 2.2 Teste: `render_report` num fixture contém as 6 seções e não contém linguagem de placar ("acerto", "acurácia")

## 3. CLI

- [x] 3.1 Ação `report` no subcomando `corpus` (+ `--out`, default `corpus-report.md`); banco vazio → falha visível com instrução de `corpus build`
- [x] 3.2 Teste/smoke: `corpus build` + `corpus report` num fixture gera o arquivo com as seções

## 4. Fechamento

- [x] 4.1 Rodar `corpus report` sobre o corpus real (n=170) e conferir sanidade dos números (cadências, trigramas, padrões do ledger ~519)
- [x] 4.2 `make test` e `make lint` verdes
- [x] 4.3 Nota curta no AGENTS.md (camada de analytics disponível; relatório é descritivo)
- [x] 4.4 `openspec archive corpus-analytics`
