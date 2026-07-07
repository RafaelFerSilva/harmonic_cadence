## 1. Fingerprint por música do DuckDB (`overlay/similarity.py`)

- [x] 1.1 `fingerprint_from_db(conn, song_id)` → monta o `Fingerprint` de `style_fingerprint` a partir de agregados: distribuição de função, matriz de transição função→função (de `chord_occurrence` ordenado por `position`), contagem de cadências (`cadence`), uso modal (`modal_coloring`), densidade de tensão (via `function_ref.is_repose`)
- [x] 1.2 Testes: dois "songs" sintéticos com a mesma sequência de função em tons diferentes → similaridade 1.0 (transposição-invariante); song_count=1

## 2. Vizinhos materializados (`overlay/similarity.py`)

- [x] 2.1 `build_neighbors(conn, k=10)`: fingerprint de todas as músicas do run corrente, cosseno par-a-par (reusa `style_fingerprint.similarity`), grava top-K em `song_neighbor` (`run_id, song_id, neighbor_id, rank, similarity`), sem auto-vizinho
- [x] 2.2 `CREATE OR REPLACE VIEW v_song_neighbor` juntando títulos + `completeness` do vizinho
- [x] 2.3 Determinismo (mesmo run → mesma tabela/ordem) e escopo run corrente (carimba `run_id`, apaga o run antes de reinserir)
- [x] 2.4 Teste de invariância: tabelas-base e views `v_gate_*`/`v_ledger_*` idênticas antes/depois

## 3. CLI `corpus similar` (`cli/main.py`)

- [x] 3.1 Ação `similar` + flags `--song <slug>` e `--k`; (re)materializa vizinhos do run corrente se ausentes/desatualizados; resolve slug→song_id
- [x] 3.2 Saída descritiva: por vizinho, similaridade + **traços compartilhados** (top funções em comum na distribuição; famílias de cadência em comum); marca vizinho de cifra parcial
- [x] 3.3 Slug inexistente → erro visível (mensagem clara), nunca silêncio
- [x] 3.4 Teste da CLI: slug conhecido lista vizinhos ordenados; slug inexistente falha visível

## 4. Verificação de método

- [x] 4.1 `songbook_baseline.py` ao vivo: 3 gates duros **293/293**, coder intocado
- [x] 4.2 `make test` e `make lint` verdes
- [x] 4.3 Rodar `harmonic corpus similar --song <slug>` end-to-end sobre o banco real e inspecionar a plausibilidade musical dos vizinhos
- [x] 4.4 Atualizar AGENTS.md/ROADMAP; sync da spec; `openspec archive` (archive+commit aguardam OK)
