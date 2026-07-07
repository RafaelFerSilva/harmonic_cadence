## 1. Modelo bilateral e bi-canal (`overlay/model.py`)

- [x] 1.1 Confirmar que `FunctionalSequenceModel` é agnóstico ao token (serve p/ grau e p/ reverso sem reescrita do núcleo de contagem)
- [x] 1.2 Adicionar um invólucro/direção reversa: treinar uma 2ª instância sobre `reversed(seq)` e mapear a surpresa reversa da posição `i` para o índice espelhado `L−1−i`
- [x] 1.3 Surpresa de canal = média(causal, reversa) em bits, respeitando fronteira de música nas duas direções
- [x] 1.4 Testes: surpresa reversa espelha corretamente; fronteira respeitada nos dois sentidos; determinismo mantido

## 2. Materialização bi-canal (`overlay/materialize.py`)

- [x] 2.1 Extrair as sequências de `function_code` e de `degree` (NULL→`∅`) por música, ordem `position`, escopo run corrente
- [x] 2.2 Treinar os 4 modelos (função fwd/bwd, grau fwd/bwd); computar `surprise_function`, `surprise_degree` e o combinado `surprise_bits` = média dos dois
- [x] 2.3 `anomaly_score` ganha colunas `surprise_function`/`surprise_degree`; DROP+recria a tabela no rebuild se o schema antigo (v1) existir (derivado, sem perda)
- [x] 2.4 `v_anomaly_worklist` expõe `degree`, `surprise_bits`, `surprise_function`, `surprise_degree` + flags de interseção; ordena por `surprise_bits` desc
- [x] 2.5 Teste de invariância: tabelas-base e views `v_gate_*`/`v_ledger_*` idênticas antes/depois

## 3. Relatório (`overlay/report.py`)

- [x] 3.1 Mostrar os componentes `surprise_function`/`surprise_degree` ao lado do combinado (denominador visível), incluindo o `degree`
- [x] 3.2 Manter guarda-corpo anti-placar e a frase "o ML rankeia, o Chediak adjudica"
- [x] 3.3 Atualizar os testes de relatório para as colunas novas

## 4. Verificação de método

- [x] 4.1 `songbook_baseline.py` ao vivo: 3 gates duros **293/293**, `function_code`/`degree` intocados
- [x] 4.2 `make test` e `make lint` verdes (ajustar os testes v1 que fixavam a semântica causal)
- [x] 4.3 Rodar `harmonic corpus anomalies` end-to-end: inspecionar a worklist bilateral e os 43 do trítono re-ranqueados
- [x] 4.4 Atualizar AGENTS.md/ROADMAP; sync da spec; `openspec archive` (archive+commit aguardam OK)
