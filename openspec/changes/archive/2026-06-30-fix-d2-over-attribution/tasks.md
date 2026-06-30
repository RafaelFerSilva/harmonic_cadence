# Tasks — fix-d2-over-attribution

> O `D2` (ii cadencial, Chediak XIX) só dispara se o dominante seguinte RESOLVER no seu alvo
> (teste intervalar). Pré-passe `ii_cadential_indices` no molde do `subv_extended_indices` +
> flag no ramo 0e. Escopo: `harmony.py` + 2 call sites + testes.

## 1. Trava de baseline (referência)

- [x] 1.1 Rodar o probe de `D2` sobre `cifras/*.md`: registrar **363 D2, 199 resolvem, 164 não**.
      Rodar `scripts/songbook_baseline.py`: trítono 62/62, diminuto 62/62 (não podem regredir).

## 2. Pré-passe de validade do `D2`

- [x] 2.1 Adicionar `ii_cadential_indices(cls, chords) -> set` em `HarmonicAnalysis` (molde do
      `subv_extended_indices`): marca `i` sse `chords[i].is_minor` + `chords[i+1].is_dominant_
      seventh` + `_get_interval(chords[i].root, chords[i+1].root) == 5` + existe `chords[i+2]` com
      raiz **ou** baixo `== (chords[i+1].root + 5) % 12` (o V resolve no alvo).

## 3. Guarda no ramo 0e + fiação

- [x] 3.1 `analyze_function`: novo param `ii_cadential: bool = False`; o ramo 0e (`harmony.py:293`)
      só emite `D2` quando `ii_cadential` é verdadeiro. Backward-compat (default False).
- [x] 3.2 Fiar os 2 call sites — `services/analysis_service.py:198` e `presentation/formatter.py:80`:
      computar `ii_idx = HarmonicAnalysis.ii_cadential_indices(all_chords)` uma vez e passar
      `i in ii_idx` (como já fazem com `i in subv_members`).

## 4. Testes

- [x] 4.1 Pré-passe + ramo: `Dm7 G7 C` → `Dm7` é `D2` (resolve); `Dm7 G7 Dm7` → `Dm7` NÃO é `D2`
      (G7 não vai a C); `Em7 A7 D7` → `Em7` é `D2` secundário (resolve em D, mesmo D7 dominante);
      `Cm7 F7 Bb` → `Cm7` é `D2` auxiliar (resolve em Bb); `Dm7 G7` no fim → NÃO `D2`.
- [x] 4.2 Ajustar testes existentes que codificavam `D2` sobre um V não-resolvente (documentar que
      era a super-atribuição); manter os de `D2` legítimo.

## 5. Gate ao vivo + zero-regressão + docs

- [x] 5.1 Re-rodar o probe de `D2`: não-resolventes **164 → 0**; resolventes **199** mantidos.
- [x] 5.2 `scripts/songbook_baseline.py`: trítono **62/62** e diminuto **62/62** (sem regressão).
- [x] 5.3 `make test` verde, `make lint` limpo.
- [x] 5.4 ROADMAP/AGENTS: marcar `fix-d2-over-attribution` fechado; notar que o invariante
      "todo `D2` resolve no alvo" está pronto p/ ser gateado no baseline (fecha o #6).
      `openspec validate fix-d2-over-attribution --strict` passa.
