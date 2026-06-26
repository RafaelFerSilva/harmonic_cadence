# Tasks — validation-harness

## 1. Lógica de medição
- [x] 1.1 `parse_key` (label → (pc, modo)) e `is_relative`.
- [x] 1.2 `evaluate_song` (detectado vs anotado) e `evaluate_corpus` (3 métricas).
- [x] 1.3 `load_corpus(dir)` lê `data/*.json` com `key`.

## 2. Verificação
- [x] 2.1 `parse_key`/`is_relative` (incl. Dó maior ≡ Lá menor).
- [x] 2.2 Agregação: `relativa-consciente >= exata`; integração em progressão clara.
- [x] 2.3 Suíte completa verde.
