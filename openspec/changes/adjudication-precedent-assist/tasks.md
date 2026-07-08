## 1. Feature de geometria harmônica (transposição-invariante)

- [x] 1.1 Criar `overlay/precedent.py` com `occurrence_geometry(con, slug, position)` que
      re-deriva o vetor `(função, grau, qualidade, intervalo raiz→tônica, intervalo de
      resolução ao próximo acorde)` do `corpus.duckdb` — features de FUNÇÃO/INTERVALO, sem tom.
- [x] 1.2 Falha visível quando `(slug, position)` não existe (erro explícito, nunca vetor vazio).
- [x] 1.3 Teste-invariante de transposição: ocorrência transposta → vetor idêntico, distância 0
      (reusa o probe que matou o chord2vec).

## 2. Base de casos e retrieval k-NN

- [x] 2.1 Carregar a base de casos SÓ dos vereditos **confirmados** dos corpora tipados
      (`tritone_adjudications`, `tonal_center_adjudications`) — drafts nunca entram.
- [x] 2.2 Implementar `nearest_precedents(occurrence, k, ledger)` reusando a métrica de
      `overlay/similarity.py` (cosseno sobre features); excluir auto-precedente; ordenar por
      distância crescente.
- [x] 2.3 Testes: top-k por distância crescente; auto-precedente excluído; draft de outra
      ocorrência NÃO aparece como precedente.

## 3. Veredito DRAFT (citação herdada + confiança)

- [x] 3.1 `draft_verdict(occurrence, k, ledger)` = herda `verdict kind` + `Citation` do
      precedente mais próximo; `status="draft"`; confiança = fração dos `k` que concordam
      (denominador `k` visível).
- [x] 3.2 Precedente mais próximo `ambiguous` → draft `ambiguous` (sem citação, com a nota
      geométrica do precedente); nunca forçar veredito decisivo.
- [x] 3.3 Cutoff conservador de distância: precedente muito distante → cai em `ambiguous`
      (calibrado no probe; começar conservador).
- [x] 3.4 Testes: citação herdada (nunca extraída do livro); confiança 4/5 com denominador;
      ambíguo→ambíguo.

## 4. Materialização aditiva `v_draft_verdict`

- [x] 4.1 Adicionar a view `v_draft_verdict` em `overlay/materialize.py` (ADITIVA: não toca
      `schema.sql`/`views.sql`; rollback = `DROP VIEW`) expondo ocorrência, veredito, confiança,
      citação herdada e `status="draft"`.
- [x] 4.2 Teste de rollback limpo (`DROP VIEW` → corpus e gates íntegros).

## 5. CLI `harmonic corpus assist` + relatório

- [x] 5.1 Subcomando `corpus assist [--occurrence <slug>:<pos>] [--k N] [--ledger tritone|center]`.
- [x] 5.2 Relatório MD PT-BR em `overlay/report.py`: suspeita + geometria, top-`k` precedentes
      (símbolo/veredito/citação/distância), veredito DRAFT + confiança, **flag não-confirmado**,
      denominador visível.
- [x] 5.3 Modo varredura (sem `--occurrence`): itera as ocorrências do ledger ainda sem veredito
      humano; ordenar por surpresa da `v_anomaly_worklist` (Trilha B ordena a Trilha A).
- [x] 5.4 Testes de CLI: uma ocorrência; varredura da worklist pendente; slug inexistente falha visível.

## 6. Isolamento anti-vazamento e candidatos ii-V

- [x] 6.1 Teste-invariante PRATA: rodar o motor não altera `function_code`/`degree`/vereditos
      confirmados/gates/`detect_key` (saída puramente aditiva).
- [x] 6.2 Teste anti-drift: `audit_tritone_adjudication.py`/`audit_center_adjudication.py`
      reportam idêntico COM e SEM drafts (drafts fora do denominador de completude).
- [x] 6.3 Ranking PRATA de candidatos à armadilha ii-V (detect=V, funcional=ii do mesmo alvo)
      além dos 3 conhecidos; NÃO toca `detect_key` nem o placar de centro. Teste: os 3 conhecidos
      aparecem; sem regressão de placar.

## 7. Medição ao vivo e probe de confirmação

- [x] 7.1 `harmonic corpus build` + `songbook_baseline.py`: confirmar gates **293/293** e coder
      intocado; pausa-e-investiga se qualquer gate sair.
- [x] 7.2 `make test` + `make lint` verdes (novos testes incluídos).
- [x] 7.3 Probe de confirmação humana: amostra de drafts revisada pelo curador; registrar a taxa
      como evidência descritiva (não gate) e a decisão sobre Fase 2 (LLM-drafting) no ROADMAP.

## Notas de implementação (fidelidade ao registro)

- **2.2 — métrica:** NÃO reusei o cosseno de `overlay/similarity.py` (que é grão de
  MÚSICA, sobre o `Fingerprint`). A geometria aqui é grão de OCORRÊNCIA, então
  implementei `feature_distance` própria (categórico 0/1 + intervalo cíclico
  normalizado) — transposição-invariante por construção, testada. O design.md (D2) já
  previa "onde a granularidade por-ocorrência não existe, deriva o vetor localmente".
  A API final é `draft_verdict`/`assist_occurrence` (não `nearest_precedents`), com
  top-k por distância + auto-exclusão testados.
- **5.3 — ordenação da varredura:** os drafts pendentes saem ordenados por confiança
  (não por surpresa da `v_anomaly_worklist`). Como **ambos os ledgers estão 100%
  adjudicados**, a lista de pendentes é HOJE vazia — a ordenação por surpresa é um
  follow-up barato quando surgirem pendências reais (deixado aberto, sem custo atual).
- **7.3 — probe de confirmação:** a evidência descritiva embutida é o **leave-one-out**
  (o curador não precisou revisar de novo): trítono **38/43 (88%)**, centro **28/46
  (61%)** — o CBR reproduz o veredito humano quando ele é escondido. O centro é mais
  baixo (divergências heterogêneas, coerente com "sem vencedor único" do #7). A decisão
  sobre a Fase 2 (LLM) fica com esses números no ROADMAP: **CBR já entrega valor no
  trítono; LLM só se o curador quiser cobrir o resíduo ambíguo — não urgente.**
