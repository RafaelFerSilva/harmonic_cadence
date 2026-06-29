## 1. Trava (antes de tocar código)

- [x] 1.1 `make test` — registrar a contagem verde (referência: 341).
- [x] 1.2 Sondagem ao vivo (feita): `C F#7 F7 E7 Eb7 D7 Db7 C` sai incoerente
  (`SubV7/IV`/`SD blues`/`T`/`SubV7/II`/`SD`/`SubV`); `F7 E7` isolado → `SD blues`.

## 2. Pré-passe de detecção de cadeia (harmony.py)

- [x] 2.1 `subv_extended_indices(chords, analysis) -> set[int]`: achar runs maximais de
  dominantes-7 consecutivos com `_get_interval(chords[i].root, chords[i+1].root) == 11`
  (semitom descendente). Para cada run de comprimento **≥3**, adicionar `{j..k-1}` (todos
  menos o último). Run de 2 → nada.
- [x] 2.2 Garantir que usa só `is_dominant_seventh` + `_get_interval` (sem novas deps).

## 3. Classificação + consistência (função, roman, escala)

- [x] 3.1 `analyze_function(..., subv_extended=False)`: no topo do bloco
  `if chord.is_dominant_seventh:`, **antes** do gate de blues (0a),
  `if subv_extended: return ("Dext", "Dominante Estendido (SubV)", <desc citando XXVIII c/d>)`.
- [x] 3.2 `roman_numeral(chord, analysis, next_chord, subv_extended=False)`: quando `True`,
  devolver `chord.symbol` (sem `V7/x`). Atualizar o wrapper `HarmonicAnalysis.roman_numeral`.
- [x] 3.3 `recommended_scale(chord, analysis, next_chord=None, subv_extended=False)` e
  `analyze_chord(..., subv_extended=False)`: quando `True`, forçar mixolídio (mesma
  precedência do `Dext` 4ªJ: vence posicional, não o alterado).
- [x] 3.4 `FUNCTION_MACRO["Dext"] = "D"` em `functional_hmm.py` (corrige o gap: hoje `"X"`).

## 4. Threading nos call sites (computar o set uma vez, consumir)

- [x] 4.1 `services/analysis_service.py`: computar `members = subv_extended_indices(all_chords,
  analysis)`; passar `i in members` em `analyze_function` (186), no comprehension de
  `chord_scales` e na seção `roman_numerals` (424).
- [x] 4.2 `domain/functional_hmm.py:280`: computar o set no parser e passar o flag.
- [x] 4.3 `presentation/formatter.py:79`: idem (computar e passar).

## 5. Testes (test_applied_dominants.py)

- [x] 5.1 Cadeia `F#7 F7 E7 Eb7 D7 Db7 C` (C maior): F#7/F7/E7/Eb7/D7 = `Dext`; `Db7` = `SubV`.
- [x] 5.2 Override de blues: `F7` dentro da cadeia = `Dext`, não `SD`.
- [x] 5.3 Par isolado `F7 E7` → `F7` = `SD` blues (não cadeia).
- [x] 5.4 Cadeia quebrada por não-dominante no meio → run termina; só ≥3 conta.
- [x] 5.5 Roman suprimido: um membro (ex. `Eb7`) → cifra simples, não `V7/x`.
- [x] 5.6 Escala: membro de cadeia → mixolídio.
- [x] 5.7 Macro HMM: `Dext` → `"D"`.

## 6. Quality gate + docs

- [x] 6.1 `make test` verde; `make lint` limpo.
- [x] 6.2 `scripts/key_baseline.py` ao vivo: **centro 95% (18/19), coleção 97%, modulantes 100%** — **idêntico** (não toca `detect_key`); zero regressão.
- [x] 6.3 `ROADMAP.md` e `AGENTS.md` (SubV estendido XXVIII c/d; fecha a porta do semitom;
  nota do fix retroativo do macro `Dext`).
- [x] 6.4 `openspec validate extended-subv --strict` passa; pronto para `openspec archive`.
