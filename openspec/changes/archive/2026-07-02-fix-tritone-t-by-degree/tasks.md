## 1. Coder

- [x] 1.1 Ramo 0f em `analyze_function` (fim da cascata de dominante-7): raiz a 9/4/3 semitons da tônica → `Dsec` deceptivo com alvo esperado `(V7/x)` (grau a 4ªJ acima da raiz), descrição citando Chediak p.114
- [x] 1.2 Garantir que II7 (pos 2) e VII7 sem resolução (pos 11) seguem fora do 0f (fall-through atual)

## 2. Testes

- [x] 2.1 `A7` sem resolução funcional em Dó → `Dsec` (V7/II), nunca `T`; idem `E7` → (V7/VI); idem `bIII7`
- [x] 2.2 `E7→Am` segue `Dsec` normal (V7/vi); `A7→Dm7` segue como antes; I7/IV7 blues intactos
- [x] 2.3 `D7`/`B7` não-resolvidos NÃO são capturados pelo 0f (seguem no fall-through)
- [x] 2.4 Último acorde da música em VI7 também vira `Dsec` deceptivo (sem next_chord)

## 3. Re-medição (política: gate quebrado = pausa-e-investiga)

- [x] 3.1 `songbook_baseline.py`: 3 gates duros PERMANECEM 170/170; ledger de trítono cai ~532→~355; registrar corroboração de centro
- [x] 3.2 `corpus build` + `gates` + `report`; comparar com o run anterior (A/B)

## 4. Fechamento

- [x] 4.1 `make test` e `make lint` verdes
- [x] 4.2 AGENTS.md/TRITONE-ADJUDICATION.md: números atualizados (follow-up 1 executado)
- [ ] 4.3 `openspec archive fix-tritone-t-by-degree`
