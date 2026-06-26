## Why

A lição da Sina: o pipeline calcula certo **dado um tom**, mas não temos como
**medir** se a detecção de tonalidade está certa. Com o tom agora capturado da
fonte (change `capture-song-key`), falta a **lógica de medição** — comparar o tom
detectado com o anotado e produzir um número de acurácia.

A medição precisa lidar com a ambiguidade **relativa maior/menor** (a Sina
expôs: nós dizemos Lá menor onde o Chediak diz Dó maior — relativas). Por isso,
três métricas, não uma.

## What Changes

- **Harness de acurácia** (`harmonic_analysis/validation/`): dado um corpus de
  `(nome, acordes, tom_anotado)`, reporta:
  - **acurácia de modo** (maior/menor);
  - **acurácia de tônica exata** (tônica + modo);
  - **acurácia relativa-consciente** (conta como acerto quando erramos só pela
    relativa maior/menor — isola o caso da Sina).
- `parse_key` (`"G"`→Sol maior, `"Am"`→Lá menor), `is_relative`, `evaluate_song`,
  `evaluate_corpus`, e `load_corpus(dir)` (lê `data/*.json` com `key`).

Fora de escopo: scrapar o corpus (precisa de rede; próximo passo); melhorar a
detecção em si (Fase B — agora com baseline pra medir).

## Capabilities

### New Capabilities
- `key-accuracy-evaluation`: harness que mede a acurácia da detecção de
  tonalidade contra tons anotados, com métrica relativa-consciente.

## Impact

- `harmonic_analysis/validation/key_accuracy.py` (novo): a lógica de medição.
- Testes: `parse_key`, `is_relative`, agregação, e integração em progressões
  claras. (O corpus real é populado pelo scraping, em seguida.)
