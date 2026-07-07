## Why

O overlay de anomalia v1 (`function-anomaly-worklist`) pontua a surpresa de cada ocorrência
por um LM **causal** sobre `function_code` — só o passado (fn₋₂, fn₋₁) e só o canal de função.
Isso deixa dois sinais de fora: (1) um acorde pode ser normal vindo da esquerda mas estranho
para o que vem **depois** (resolução atípica) — a surpresa causal não vê; (2) uma função comum
num **grau** incomum (ex.: um dominante sobre um grau raro) não é flagada, porque o grau não
entra no modelo. Enriquecer o overlay com contexto **bilateral** e um **canal de grau** afia a
worklist que alimenta a adjudicação Chediak (Trilha A), sem sair da lei de ouro (PRATA).

## What Changes

- **Surpresa bilateral:** além do modelo causal (esquerda→direita), um modelo **backward**
  (direita→esquerda, mesmas contagens sobre sequências revertidas). A surpresa de função de cada
  ocorrência passa a ser a média das duas direções (bits) — um acorde só é fortemente anômalo se
  surpreende dos **dois** lados. Fronteira de música segue respeitada em ambas as direções.
- **Canal de grau:** um segundo modelo bilateral sobre o `degree` (grau em algarismo romano;
  `NULL` → token sentinela `∅`, que é informativo). Produz uma surpresa de grau independente.
- **Escore combinado:** `surprise_bits` passa a ser a média da surpresa de função e da de grau,
  com **os dois componentes visíveis** na worklist (denominador/interpretabilidade). A ordenação
  usa o combinado; nada vira caixa-preta.
- A view `v_anomaly_worklist` ganha as colunas `surprise_function`, `surprise_degree` (e mantém
  `surprise_bits` como o combinado). O relatório mostra os componentes.
- **BREAKING (interno):** a semântica de `surprise_bits` muda (causal-função → média bilateral
  função+grau) e a tabela `anomaly_score` ganha colunas. É derivado/regenerável — sem migração de
  dado externo; rematerializa com `harmonic corpus anomalies`.

## Capabilities

### New Capabilities
<!-- Nenhuma capability nova. -->

### Modified Capabilities
- `functional-anomaly-overlay`: o requisito do modelo passa de causal-função para **bilateral +
  canal de grau**; o requisito do escore/worklist ganha os componentes de função e grau visíveis.

## Impact

- **Código:** `overlay/model.py` (generaliza para bilateral + treino sobre qualquer canal),
  `overlay/materialize.py` (2 canais, colunas novas na tabela/view), `overlay/report.py`
  (componentes visíveis). Testes novos + ajuste dos existentes que fixam a semântica causal.
- **Banco:** colunas novas em `anomaly_score` + view `v_anomaly_worklist` (aditivo/derivado;
  rollback = DROP e rematerializar v1).
- **Não toca:** os 3 gates duros (293/293), o `detect_key`, o `function_code`/`degree` do coder
  (o overlay só LÊ), nem a persistência base. Mede contra `songbook_baseline.py` ao vivo.
- **Sem dependência nova:** stdlib (`math`) + contagem; segue interpretável sobre vocabulários
  pequenos (12 funções, ~19 graus com `∅`).
