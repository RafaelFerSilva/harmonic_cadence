# Tasks — ingest-songbook-vols-2-5

## 1. Preparação

- [x] 1.1 Backup local `cifras/.bak-<data>/` (cópia integral antes do primeiro write)
- [x] 1.2 Enumeração do Vol. 2: transcrever a lista-alvo do índice-irmão (Vol. 1, PDF
      pp.4–5) para uma worklist com slugs; checar colisões de slug contra `cifras/`
      existente (colisão = investigar antes de transcrever, D5)
- [x] 1.3 Enumeração do Vol. 5: transcrever o mapa página→música do índice próprio
      (PDF pp.3–4); marcar entradas borradas como "recuperar na varredura"; checar
      colisões de slug
- [x] 1.4 Calibrar o offset do Vol. 5 (achar a 1ª música do índice no PDF e fixar
      `PDF = livro − k`); confirmar o offset −25 do Vol. 2 numa segunda música
- [x] 1.5 Verificador de lote: rotina (reuso do critério do `audit_completeness.py`)
      que, dado um `cifras/<slug>.md` novo + diagramas transcritos, valida
      `extract_chords_from_lines ⊇ diagramas` com normalização de grafia (D3)

## 2. Ingestão Vol. 2 (60 músicas reais — COMPLETO)

- [x] 2.1–2.4 Transcritas todas as 60 do Vol. 2 (46 sessão anterior + 14 em 2026-07-05),
      via varredura sequencial completa do PDF (livro pp.26–143). Cada uma verificada
      (`verify_transcription.py` = `ok`). Detalhes/decisões em `INGESTION-DECISIONS.md`.
- [x] 2.5 Fechamento do Vol. 2: worklist × PDF reconciliada — **2 fantasmas** do índice-irmão
      (`se-e-tarde-me-perdoa`, "Eu sei que…") NÃO existem no volume (marcados `[!]`); Vol.2
      real = 60. Baseline: **gates duros 231/231 verdes** (diminuto/D2/cadência); centro
      170/207 (82%); ledger trítono 32. 496 testes verdes. Sem regressão.

## 3. Ingestão Vol. 5 (63 músicas, lotes de ~10–15)

- [ ] 3.1 Lote 5.A: transcrever, verificar, riscar (miolo decide sobre o índice)
- [ ] 3.2 Lote 5.B: idem
- [ ] 3.3 Lote 5.C: idem
- [ ] 3.4 Lote 5.D: idem (até esgotar; páginas ilegíveis viram pendência com página,
      nunca palpite)
- [ ] 3.5 Fechamento do Vol. 5: reconciliar índice × miolo; baseline — gates duros 100%

## 4. Re-medição e fatos (Vol. 2 — feito; refazer ao fim do Vol. 5)

- [x] 4.1 `audit_completeness.py` sobre o corpus ampliado (n=231): **SEM drift**; as 14 novas
      entram `complete`.
- [ ] 4.2 `harmonic corpus build` + `corpus gates` + `corpus report` — **adiado p/ o fim da change**
      (após o Vol. 5): o build DuckDB é caro (~4-6 min) e faz mais sentido materializar o corpus
      final de uma vez. Baseline funcional ao vivo já cobre os gates neste checkpoint.
- [x] 4.3 Números novos registrados (gates 231/231, centro 170/207, ledger trítono 32) em
      `INGESTION-DECISIONS.md` e ROADMAP/AGENTS.
- [x] 4.4 `make test` — **496 verdes** (sem mudança de motor).

## 5. Documentação

- [x] 5.1 Fato do Vol. 1 corrigido em AGENTS.md e ROADMAP.md (Vol. 1 = corpus original n=62,
      proveniência = conversão antiga; risco na auditoria ampla).
- [x] 5.2 Estado/números atualizados em AGENTS.md (#8: 62→119→170→231) e ROADMAP.md (bloco
      "Status 2026-07-05" + próximos passos = só Vol. 5).
- [x] 5.3 Decisões de colisão/pendência registradas em `INGESTION-DECISIONS.md`.
