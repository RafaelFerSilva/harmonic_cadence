# Tasks — pipeline-observability

## 1. Infra
- [x] 1.1 Logger de módulo; trocar `print("Aviso:")` por `logger.warning`.
- [x] 1.2 `_safe_section(result, name, compute, default)` (loga + diagnostics).
- [x] 1.3 `result["diagnostics"] = []` inicializado no resultado.

## 2. Aplicar
- [x] 2.1 As 8 seções (modal, roman, voice_leading, chord_scales, functional_parse,
      reharmonizations, explanation, tonal_regions) via `_safe_section`.
- [x] 2.2 JSON expõe `diagnostics`.

## 3. Verificação
- [x] 3.1 Run limpo → `diagnostics == []`.
- [x] 3.2 Seção que estoura → registrada em diagnostics + default + log; resto ok.
- [x] 3.3 Suíte completa verde.
