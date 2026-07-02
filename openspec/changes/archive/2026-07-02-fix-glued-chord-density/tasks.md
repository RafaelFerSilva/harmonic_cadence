## 1. Fix no cifra_core

- [x] 1.1 `lines.py`: helper `_glued_chord_token` (≥1 acorde válido + resíduo vazio após remover acordes e decoração — reusa `_RESIDUE_DECOR`/`ChordPattern.CHORD.sub`, cláusula (d) invertida)
- [x] 1.2 `classify_line`: somar `_glued_chord_token` ao predicado de posição-de-acorde da densidade
- [x] 1.3 Generalizar decoração pura no denominador (token `^[/|%\-—·]+$` não conta — cobre `///`)

## 2. Testes (cifra_core)

- [x] 2.1 Linha real do dindi (`C#m7 /  Am6/  … Bm7/ / /  Gm6/ / /`) → CHORD; extração devolve todos os acordes
- [x] 2.2 Palavra de letra com prefixo-acorde (`Dado/`, `Brasil`) NÃO conta como posição-de-acorde; linhas de prosa seguem LYRIC
- [x] 2.3 Token só-decoração (`///`) fora do denominador
- [x] 2.4 Regressão: cenários existentes (malformado `D9/S`, colado `Gm7(11)///Gb7(#11)///`, idempotência) seguem verdes

## 3. Re-medição (política D4: gate quebrado = pausa-e-investiga)

- [x] 3.1 `songbook_baseline.py` no corpus (n=170): 3 gates duros PERMANECEM 170/170; registrar novos números de corroboração de centro e ledger de trítono
- [x] 3.2 `harmonic corpus build` (novo `analysis_run`) + `corpus gates` verde + `corpus report`; comparar ledger/centro com o run anterior
- [x] 3.3 Confirmar recuperação: dindi/samba-em-preludio ganham os acordes de volta (n_chords sobe; divergência manifesto×corpo da auditoria cai)
- [x] 3.4 (descoberto em 3.2) Views de gate/ledger/analytics escopadas ao RUN CORRENTE — com 2+ runs no banco, `corpus gates`/`report` somavam os snapshots (agree=248, ledger=1051); `v_song_current` + joins; teste de duplo-build

## 4. Fechamento

- [x] 4.1 `make test` e `make lint` verdes
- [x] 4.2 AGENTS.md/ROADMAP: atualizar números movidos (centro, ledger) citando esta change
- [ ] 4.3 `openspec archive fix-glued-chord-density`
