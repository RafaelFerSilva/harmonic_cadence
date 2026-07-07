## 1. Critério de ligação parametrizável (`overlay/clustering.py`)

- [x] 1.1 `_agglomerate` recebe `linkage` (`average`|`complete`); injeta a agregação das similaridades par-a-par (média vs. mínimo→distância máxima); laço de fusão inalterado
- [x] 1.2 `build_clusters(conn, k, linkage='average')` propaga o parâmetro; `average` é o default (compatível)
- [x] 1.3 Testes: `complete` é determinístico; a maior família em `complete` ≤ maior família em `average` (mesmo k); músicas idênticas juntas nos dois linkages

## 2. CLI (`cli/main.py`)

- [x] 2.1 Flag `--linkage {average,complete}` (default `average`) no `corpus`; `clusters` passa ao `build_clusters` e reporta o linkage usado
- [x] 2.2 Guarda-corpo mantido (sem placar, sem "k/linkage ótimo")

## 3. Verificação de método

- [x] 3.1 `songbook_baseline.py` ao vivo: 3 gates duros **293/293**, coder intocado
- [x] 3.2 `make test` e `make lint` verdes
- [x] 3.3 Rodar `harmonic corpus clusters --k 8 --linkage complete` end-to-end: comparar tamanhos vs. `average` (o núcleo-247 deve quebrar em famílias mais equilibradas)
- [x] 3.4 Atualizar AGENTS.md/ROADMAP; sync da spec; `openspec archive` (archive+commit aguardam OK)
