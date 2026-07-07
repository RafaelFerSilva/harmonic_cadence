## 1. Implementar o Path D (bracket)

- [x] 1.1 Em `domain/key_detection.py`: nova função `_ii_v_bracket_path(symbols, ks_best)` que (a) checa pré-condições baratas (X=(Y−7); ≥2 V7/SubV7→X; X presente como repouso ≥1; X≠Y); (b) só então importa tardiamente `chediak_functional_center` e confirma que o funcional é o **ii de X** (raiz X+2, menor); (c) retorna `(X, _x_mode(present,X))` ou `None`.
- [x] 1.2 Wiring no `detect_key`: aplicar `_ii_v_bracket_path` após o bloco do `_tritone_gate` e antes do `_i7_funk_anchor_path` (mesmo padrão de aplicação: só sobrepõe se ≠ atual; recomputa `best_score`).
- [x] 1.3 Docstring do path citando Chediak pp.84-85 + o achado #7 (por que precisa do funcional); nota de que consulta o achador funcional (exceção aos A/B/C estruturais), import tardio, sem ciclo/recursão.

## 2. Testes

- [x] 2.1 Teste unitário: `bolinha-de-sabao`/`menina` (`Dm7 G7 C…` → C) e `rio` (`Gm7 C7 F…` → F) corrigidos pelo Path D; um caso de controle que NÃO é bracket (ex. progressão ii-V-do-IV sintética) NÃO é tocado.
- [x] 2.2 Teste anti-regressão sobre o corpus (`cifras/*.md`): o CONJUNTO de músicas cujo `detect_key` muda por causa do Path D é EXATAMENTE {bolinha-de-sabao, menina, rio} — trava o zero-regressão (dente: pega qualquer novo falso-positivo).

## 3. Verificação ao vivo

- [x] 3.1 `uv run python scripts/songbook_baseline.py`: 3 gates duros **293/293**; corroboração de centro **216/262 inalterada** (o gate corrige o detector, não o placar); os 8 `detect`-certos e os 216 agree intactos.
- [x] 3.2 Rebuild `harmonic corpus build` + `corpus gates`: gates verdes; conferir que `bolinha`/`menina`/`rio` agora têm `detected_key` = Dó/Dó/Fá (e seguem `diverge`, pois o funcional é o ii).
- [x] 3.3 `make test` e `make lint` verdes.

## 4. Fecho

- [x] 4.1 Atualizar AGENTS.md/ROADMAP: Path D (bracket ii-V) fechado; nota de que corrige o detector sem mover o placar; follow-up (achador funcional) registrado.
- [ ] 4.2 `openspec archive add-ii-v-bracket-center-path` após validação (com sync das specs).
