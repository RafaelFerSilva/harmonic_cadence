## 1. Corrigir os acessores (gates passam a executar)

- [x] 1.1 `_dominant_invariant`: trocar `Chord(sym).get_category().value == "dominant"` por `Chord(sym).quality == "dominant"`
- [x] 1.2 `_diminished_invariant`: trocar `Chord(sym).get_category().value == "diminished"` por `Chord(sym).quality == "diminished"`
- [x] 1.3 `_d2_resolution_invariant`: trocar `tgt.bass` por `tgt.properties.bass`
- [x] 1.4 Verificar empiricamente: diminuto=0, D2=0, cadência=0 (gates verdes reais); trítono>0 (executa)

## 2. Isenção I7-tônica + reframe do trítono como ledger

- [x] 2.1 `_dominant_invariant`: isentar a classe limpa — se `quality=="dominant"` e função-alvo não-dominante E `degree_base(degree) in ("I","i")` e code=="T", NÃO é violação (I7-tônica, `i7-funk-anchor`)
- [x] 2.2 Renomear a função para refletir intenção (ex.: `_tritone_nondominant_ledger`) e ajustar o retorno para o ledger afiado (~519)
- [x] 2.3 `main()`: reframe da seção de trítono de "INVARIANTE (born-green)" para "LEDGER de curadoria (pós-isenção I7)" — reporta contagem, não pass/fail
- [x] 2.4 Verificar: ledger do baseline ≈ 519 (não 944, não 0)

## 3. Afiar a view de ledger na persistência (mesma isenção)

- [x] 3.1 `persistence/views.sql`: `v_ledger_tritone_nondominant` ganha `AND NOT (o.function_code='T' AND o.degree IN ('I','i'))`
- [x] 3.2 Verificar paridade: contagem da view ≈ contagem do baseline afiado sobre o mesmo corpus

## 4. Testes

- [x] 4.1 Teste: os 3 gates duros (diminuto/D2/cadência) executam e são verdes num fixture
- [x] 4.2 Teste: um fixture com `A7` como tônica (grau I, função T) NÃO entra no ledger de trítono; um `E7→T` em grau não-tônica (forçado) entra
- [x] 4.3 Teste: a view `v_ledger_tritone_nondominant` aplica a isenção I7 (não lista degree I/i com função T)

## 5. Documentação

- [x] 5.1 AGENTS.md: corrigir a narrativa (diminuto vira gate verde real; trítono é ledger afiado ~519; não mais "170/170" vacuoso)
- [x] 5.2 ROADMAP.md: atualizar o estado dos gates funcionais

## 6. Fechamento

- [x] 6.1 `make test` e `make lint` verdes
- [ ] 6.2 `openspec archive fix-baseline-noop-gates`
