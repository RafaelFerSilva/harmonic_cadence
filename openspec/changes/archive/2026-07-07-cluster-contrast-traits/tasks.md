## 1. Traços por contraste (`overlay/clustering.py`)

- [x] 1.1 `corpus_baseline(conn)`: participação média de cada função e taxa de cada família de cadência por música no run corrente (computado uma vez)
- [x] 1.2 `cluster_traits` vira contraste: lift = média_família − média_corpus, por função e cadência; retorna os de lift > 0 ordenados desc, com o valor do lift; lista vazia se a família é o baseline
- [x] 1.3 Testes: função sobre-representada aparece com lift > 0; família que espelha o corpus → sem traços distintivos (baseline)

## 2. Saída da CLI (`cli/main.py`)

- [x] 2.1 `corpus clusters` mostra os traços por contraste com o valor do lift; sinaliza "família-baseline" quando não há traço acima da média
- [x] 2.2 Guarda-corpo mantido (sem placar, sem "k ótimo")

## 3. Verificação de método

- [x] 3.1 `songbook_baseline.py` ao vivo: 3 gates duros **293/293**, coder intocado
- [x] 3.2 `make test` e `make lint` verdes (ajustar os testes de traço absoluto do clustering)
- [x] 3.3 Rodar `harmonic corpus clusters --k 8` end-to-end: as famílias-satélite mostram seu dialeto (Emp/Dsec/…) por contraste; o núcleo é sinalizado como baseline
- [x] 3.4 Atualizar AGENTS.md/ROADMAP; sync da spec; `openspec archive` (archive+commit aguardam OK)
