## 1. Probe read-only (fundação de dado)

- [x] 1.1 Confirmar o grão e a ordenação das sequências: `chord_occurrence` por `song_id` ordenado por `position`, com fronteiras de música limpas (sem sequência cruzando `song_id`)
- [x] 1.2 Medir cobertura de contexto de bigrama vs. trigrama no run corrente (quantos contextos têm contagem ≥ k) para decidir a ordem do n-grama sem tuning por acurácia
- [x] 1.3 Verificar que `v_ledger_tritone_nondominant` e `v_center_ledger` expõem chave utilizável (`song_id`,`position` / `center_status`) para o cruzamento

## 2. Modelo de sequência funcional (`overlay/model.py`)

- [x] 2.1 Criar subpacote `harmonic_analysis/overlay/` (`__init__.py`)
- [x] 2.2 Extrair sequências de `function_code` por música (ordem `position`), sem cruzar fronteira de música
- [x] 2.3 Contar unigrama/bigrama/trigrama e implementar backoff suavizado (Witten-Bell) — probabilidade condicional sem P=0 para contexto não visto
- [x] 2.4 Computar surpresa por ocorrência = −log P(fn | contexto) em unidade declarada (bits), determinística para um run
- [x] 2.5 Testes de unidade: suavização sem zero, determinismo (mesmo run → mesma ordem), fronteira de música respeitada

## 3. Materialização no DuckDB (`overlay/materialize.py`)

- [x] 3.1 Gravar tabela de escores por ocorrência carimbada com `run_id`/`engine_version`; falha-rápido se o run não existir
- [x] 3.2 `CREATE OR REPLACE VIEW v_anomaly_worklist` com `song_id, position, symbol, function_code, surprise` + flags de interseção (`in_tritone_ledger`, `in_center_diverge`)
- [x] 3.3 Garantir que a materialização NÃO altera as 11 tabelas-base nem as views `v_gate_*`/`v_ledger_*` (teste de invariância pós-rebuild)

## 4. Relatório e CLI (`overlay/report.py` + `cli/main.py`)

- [x] 4.1 Relatório Markdown PT-BR a partir de `v_anomaly_worklist`: top-N ocorrências surpreendentes, **denominadores visíveis** (total, na worklist, cobertura), contagem observada ao lado da surpresa
- [x] 4.2 Seção que destaca as interseções com trítono (43) e centro-diverge (46) — a priorização que une Trilha B → Trilha A
- [x] 4.3 Frase fixa declarando "o ML rankeia, o Chediak adjudica"; herdar o guarda-corpo anti-placar do `corpus report`
- [x] 4.4 Subcomando `harmonic corpus anomalies` ao lado de `corpus build|gates|report`
- [x] 4.5 Teste do guarda-corpo: falha se aparecer vocabulário de placar (acurácia/precisão/score-como-verdade)

## 5. Verificação de método (invariante do projeto)

- [x] 5.1 Rodar `songbook_baseline.py` ao vivo: os 3 gates duros seguem **293/293** e nenhum `function_code` foi alterado
- [x] 5.2 `make test` (510 verdes) e `make lint` (overlay limpo) verdes
- [x] 5.3 Rodar `harmonic corpus anomalies` end-to-end e inspecionar a worklist: as 43 ocorrências do ledger de trítono aparecem priorizadas por surpresa (seção 2a)
- [x] 5.4 Atualizar AGENTS.md ("Estado atual") e ROADMAP com o resultado; `openspec archive` da change (archive + commit aguardam OK do usuário)
