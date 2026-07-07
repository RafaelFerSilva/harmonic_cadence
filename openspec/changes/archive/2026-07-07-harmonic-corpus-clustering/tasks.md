## 1. Agrupamento aglomerativo (`overlay/clustering.py`)

- [x] 1.1 Vetorizar cada música do run corrente num eixo de funções GLOBAL (reusa `fingerprint_from_db` + `style_fingerprint._feature_vector`); matriz de similaridade de cosseno par-a-par
- [x] 1.2 Aglomerativo *average-linkage* puro-Python até `k` famílias (determinístico, desempate por `song_id`)
- [x] 1.3 Medoid por família = maior similaridade média intra-família (família unitária → ela mesma)
- [x] 1.4 Testes: k famílias sobre M músicas (cada música em 1 família); determinismo (mesmo run+k → idêntico); músicas idênticas na mesma família; medoid é o centro

## 2. Materialização (`overlay/clustering.py`)

- [x] 2.1 `build_clusters(conn, k)`: grava `song_cluster` (`run_id, song_id, cluster_id, is_medoid`), carimba run, apaga o run antes de reinserir
- [x] 2.2 `CREATE OR REPLACE VIEW v_song_cluster` juntando títulos + `completeness`
- [x] 2.3 Teste de invariância: tabelas-base e views `v_gate_*`/`v_ledger_*` idênticas antes/depois

## 3. CLI `corpus clusters` (`cli/main.py`)

- [x] 3.1 Ação `clusters` + flag `--k` (reaproveita a `--k` do `similar`); (re)materializa para o `k` pedido
- [x] 3.2 Saída descritiva por família: tamanho, protótipo (medoid), membros, e traços salientes (top funções/cadências agregadas); marca membros de cifra parcial
- [x] 3.3 Guarda-corpo: sem vocabulário de placar, sem alegar "k ótimo"
- [x] 3.4 Teste da CLI/saída: k famílias listadas com protótipo; texto descritivo (anti-placar)

## 4. Verificação de método

- [x] 4.1 `songbook_baseline.py` ao vivo: 3 gates duros **293/293**, coder intocado
- [x] 4.2 `make test` e `make lint` verdes
- [x] 4.3 Rodar `harmonic corpus clusters --k 8` end-to-end sobre o banco real e inspecionar a plausibilidade musical das famílias/protótipos
- [x] 4.4 Atualizar AGENTS.md/ROADMAP; sync da spec; `openspec archive` (archive+commit aguardam OK)
