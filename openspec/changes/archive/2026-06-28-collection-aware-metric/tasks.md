## 1. same_collection + KeyEval (key_accuracy.py)

- [x] 1.1 Em `packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py`, adicionar `MAJOR_OFFSETS = frozenset({0,2,4,5,7,9,11})` e `MINOR_OFFSETS = frozenset({0,2,3,5,7,8,10})` e a função `same_collection(gold: Key, detected: Key) -> bool` que retorna `(detected[0] - gold[0]) % 12 in (MAJOR_OFFSETS if gold[1] == "major" else MINOR_OFFSETS)`
- [x] 1.2 Adicionar o campo `same_collection: bool` ao dataclass `KeyEval`
- [x] 1.3 Em `evaluate_song`, preencher `same_collection=same_collection(annotated, detected)`
- [x] 1.4 Em `evaluate_corpus`, agregar `"collection_accuracy": sum(e.same_collection for e in evals) / denom`
- [x] 1.5 Exportar `same_collection` em `validation/__init__.py` (`import` + `__all__`)

## 2. 4ª métrica e verdict no baseline (key_baseline.py)

- [x] 2.1 Em `scripts/key_baseline.py`, importar `same_collection` de `harmonic_analysis.validation`
- [x] 2.2 Calcular `coll = sum(same_collection(a, d) for _, a, d in results) / n` (só nas monotonais, mesmo denominador das outras 3)
- [x] 2.3 Na função de verdict por música, inserir o nível "coleção" antes de "ERRO": se não é exato/relativo/modo-ok mas `same_collection(a, d)` é True → verdict `"coleção"`; senão `"ERRO"` (= coleção errada de fato)
- [x] 2.4 Imprimir a 4ª linha agregada: `coleção (armadura):  NN%`

## 3. Testes

- [x] 3.1 Em `packages/harmonic_analysis/tests/test_key_accuracy.py`, testar `same_collection`: mediante (C maior → E, offset 4) True; dominante (C maior → G, offset 7) True; relativa (C maior → A, offset 9) True; cromático (A maior → C, offset 3) False; gold menor (Am → grau diatônico) True/False conforme offset
- [x] 3.2 Testar que `evaluate_song` preenche `same_collection` e que `evaluate_corpus` expõe `collection_accuracy`
- [x] 3.3 Testar a invariante de aninhamento num corpus sintético: `exact_accuracy <= relative_aware_accuracy <= collection_accuracy`

## 4. ROADMAP e validação

- [x] 4.1 Rodar `make test` (todos verdes) e `make lint`
- [x] 4.2 Rodar `uv run python scripts/key_baseline.py` (rede): confirmar a 4ª linha "coleção (armadura)" (~95% esperado) e os verdicts "coleção" nas falhas de centro; documentar os 4 números no `ROADMAP.md`
- [x] 4.3 Atualizar `ROADMAP.md`: Incremento 3a (`collection-aware-metric`) feito; Incremento 3b (arbitragem modal↔tonal de centro) registrado como **bloqueado** — sem discriminador modal preciso (`detect_mode`/`church_mode` é ruído: frígio em 52/60, candidato a conserto/remoção separado)
