## 1. Coder (harmony.py)

- [x] 1.1 Mover o sub-ramo `Dsec`-por-resolução (ni==5, alvo não-tônica) para ANTES do Emp bVII7/bVI7 (resolução precede empréstimo; D1)
- [x] 1.2 Ramo II7: pos 2 no fall-through → `SD` "Subdominante alterada (II7)" (quadro p.113)
- [x] 1.3 Ramo VII7 sem resolução no I: pos 11 no fall-through → `Dsec` "(V7/III) deceptivo" (p.112(2)/p.114)

## 2. Isenções citáveis no ledger

- [x] 2.1 `songbook_baseline.py` `_tritone_nondominant_ledger`: isentar (função, grau) documentados — `T`/I (existe), `SD`/IV, `SD`/II, `Emp` (quadro p.113)
- [x] 2.2 `persistence/views.sql` `v_ledger_tritone_nondominant`: as MESMAS isenções
- [x] 2.3 Teste-invariante: o coder só emite `Emp` de qualidade dominante nas posições 10/8 (trava a isenção ampla de Emp; D4)

## 3. Testes

- [x] 3.1 Tom menor: `bVII7→bIII` diatônico vira `Dsec (V7/III)`; tom maior: `Bb7→C` segue `Emp` (D5)
- [x] 3.2 `D7→C7M` em Dó → `SD` alterada; `D7→G7M` segue `Dsec (V7/V)` (resolução intocada)
- [x] 3.3 `B7→C` segue `D` cadencial; `B7→F7M` vira `Dsec (V7/III)`
- [x] 3.4 Regressão: blues I7/IV7, SubV, Daux, Dext, 0f intocados

## 4. Re-medição (pausa-e-investiga)

- [x] 4.1 `songbook_baseline.py`: 3 gates duros 170/170; ledger ~318→~25-90; corroboração registrada
- [x] 4.2 `corpus build` + `gates` + `report`; padrões restantes = só ambíguos honestos (bV7, resíduos)

## 5. Fechamento

- [x] 5.1 `make test` e `make lint` verdes
- [x] 5.2 AGENTS.md + TRITONE-ADJUDICATION.md: adjudicação COMPLETA (follow-ups 1 e 2 executados; residual final documentado)
- [x] 5.3 `openspec archive classify-special-function-dominants`
