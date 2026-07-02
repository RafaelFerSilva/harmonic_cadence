## 1. Preparação

- [x] 1.1 Backup local `cifras/.bak-2026-07-02/` das 15 (rollback barato)
- [x] 1.2 Mapa slug→página do livro→página do PDF (offset −20) das 15

## 2. Re-transcrição (lotes, com verificação por música — D2)

- [x] 2.1 Lote 1: a-paz (32), a-tarde (34), ainda-mais-lindo (36)
- [x] 2.2 Lote 2: brisa-do-mar (50), beijo-partido (52), embarcacao (76)
- [x] 2.3 Lote 3: estrada-branca (84), gaiolas-abertas (92), luiza (94)
- [x] 2.4 Lote 4: no-cordao-da-saideira (102), se-todos-fossem-iguais-a-voce (132), seu-chopin-desculpe (134)
- [x] 2.5 Lote 5: tempo-feliz (142), viola-enluarada (148), ultima-forma (150)
- [x] 2.6 Verificação mecânica: p/ cada uma, extração ⊇ diagramas do livro (script ad hoc)

## 3. Ledger + auditoria

- [x] 3.1 Remover as 15 de `_INCOMPLETE` no `completeness.py` + nota de proveniência (D3)
- [x] 3.2 `audit_completeness.py`: sem drift (as 15 não acusam; as 13 suspect intactas)

## 4. Re-medição

- [x] 4.1 `songbook_baseline.py`: gates duros 170/170; registrar centro/ledger de trítono
- [x] 4.2 `corpus build` + `gates` + `report`: completeness incomplete=0, suspect=13

## 5. Fechamento

- [x] 5.1 `make test` + `make lint` verdes
- [x] 5.2 AGENTS.md: quarentena v4 resolvida pela fonte; risco registrado (outras ~36 do v4 sem auditoria contra o livro)
- [x] 5.3 `openspec archive retranscribe-v4-quarantined`
