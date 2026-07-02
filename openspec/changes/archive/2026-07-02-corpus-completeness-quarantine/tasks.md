## 1. Re-auditoria pós-fix (insumo da curadoria)

- [x] 1.1 Re-rodar a auditoria declarado×extraído sobre `cifras/*.md` com a extração corrente, descontando dialeto (mesmos pitch-classes via parse) e mojibake (`FO`≈`F°`) — lista final de `suspect`
- [x] 1.2 Re-rodar o cruzamento v4 (`Acordes:` do livro × corpo do fence) — lista final de `incomplete` (com os símbolos ausentes por música)

## 2. Ledger curado

- [x] 2.1 `harmonic_analysis/corpus/completeness.py`: `CompletenessEvidence` (+`__post_init__` falha-rápido) e `CompletenessFact` tipados, no padrão do `modal_centers`; dict por slug + `completeness_for(slug)`
- [x] 2.2 Popular com os fatos curados de 1.1/1.2 (só slug+símbolos+evidência; conservador — na dúvida, fica fora)
- [x] 2.3 Teste-invariante: fato sem evidência/sem ausentes falha na importação; lookup por slug funciona; nenhum texto de cifra no módulo

## 3. Script de auditoria

- [x] 3.1 `scripts/audit_completeness.py`: re-deriva evidência (manifesto do arquivo + header do livro se a fonte v4 existir), desconta dialeto, compara com o ledger e reporta drift nas duas direções; sem `cifras/` → aviso e exit 0
- [x] 3.2 Rodar e conferir: ledger×auditoria sem divergência no estado atual

## 4. Persistência + report

- [x] 4.1 `schema.sql`: coluna `song.completeness TEXT NOT NULL DEFAULT 'complete'`
- [x] 4.2 `materialize.py`: estampa por slug via ledger
- [x] 4.3 `report.py`: contagem por status na seção 1; marcação de quarentena na worklist do trítono (seção 6)
- [x] 4.4 Testes: estampagem (fixture com slug quarentenado), report mostra contagem, gates NÃO filtram (ocorrência de música quarentenada segue avaliada)

## 5. Fechamento

- [x] 5.1 `corpus build` + `report` no corpus real; conferir contagens (16 incomplete + suspects da re-auditoria)
- [x] 5.2 `make test` e `make lint` verdes
- [x] 5.3 Nota no AGENTS.md (quarentena de completude; v3 = ponto cego declarado)
- [x] 5.4 `openspec archive corpus-completeness-quarantine`
