## 1. Trava (antes de tocar código)

- [x] 1.1 Rodar `make test` e registrar a contagem verde (referência da suíte).
- [x] 1.2 Anotar o comportamento atual dos 3 tipos (sondagem): descendente/auxiliar → `Emp`; ascendente → `Dsec`/`D`; `vii°7` → `D`.

## 2. Classificação do diminuto não-dominante (harmony.py)

- [x] 2.1 Em `analyze_function`, adicionar o ramo `0d` (após o bloco `0c` do dim7-dominante, antes da seção 1/5b): `if chord.quality == "diminished":` classifica e retorna code `"Dim"` com nome/descrição do subtipo.
- [x] 2.2 Subtipos pela motion da fundamental: **auxiliar** (`_get_interval(prev.root, next.root) == 0`), **descendente** (`_get_interval(next.root, chord.root) == 1`), **genérico** ("Diminuto" conectivo/de passagem) para o resto. Auxiliar tem precedência.
- [x] 2.3 Preservar o ascendente→dominante (`0c`) e o `vii°7` — não reclassificar.
- [x] 2.4 Remover o bloco morto `if func_code == "Dim": ...` da seção 1 (ofuscado pelo `0c`).

## 3. Testes

- [x] 3.1 `Ab°7→G` e `Dm Db°7 C` → diminuto **descendente**, NÃO `Emp`.
- [x] 3.2 `C C#°7 C` e `Dm D#°7 Dm` → diminuto **auxiliar**, NÃO `Emp`.
- [x] 3.3 `C#°7→Dm` segue `Dsec` (V7(b9)/ii); `B°7→C` segue `D`.
- [x] 3.4 Invariante: nenhum diminuto retorna code `Emp`.

## 4. Quality gate + docs

- [x] 4.1 `make test` verde; `make lint` limpo.
- [x] 4.2 Rodar `scripts/key_baseline.py` ao vivo (sanidade): baseline **idêntico** (a change não toca `detect_key`).
- [x] 4.3 Atualizar `ROADMAP.md` (classificação completa do diminuto: ascendente=dominante + descendente + auxiliar; cita Chediak pp.102–104).
- [x] 4.4 `openspec validate classify-diminished-chords --strict` passa; pronto para `openspec archive`.
