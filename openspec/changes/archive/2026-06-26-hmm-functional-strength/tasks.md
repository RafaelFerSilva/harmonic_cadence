# Tasks — hmm-functional-strength

## 1. Emissão ponderada
- [x] 1.1 `STRENGTH_MASS` (strong/medium/weak/None) e `_emission(macro, strength)`.
- [x] 1.2 `parse_codes(codes, symbols, strengths=None)` — emissão por acorde.

## 2. Fornecer a força
- [x] 2.1 `build_functional_parse` lê `strength` dos dicts da análise.
- [x] 2.2 `parse_progression` deriva a força do grau (`functional_strength`).

## 3. Verificação
- [x] 3.1 Força forte concentra (confiança ↑); fraca espalha (alternativas).
- [x] 3.2 Parse só-código (sem força) inalterado; determinismo preservado.
- [x] 3.3 Suíte completa verde.
