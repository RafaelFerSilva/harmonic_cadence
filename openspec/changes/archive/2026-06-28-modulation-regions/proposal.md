## Why

Wave e Chega de Saudade (Tom Jobim) são músicas bitonais reais: modulam entre Ré menor (abertura/verso) e Ré maior (refrão) via acorde pivô A7, que funciona simultaneamente como V7 de ambas as tonalidades — modulação tipo B por acorde pivô segundo Chediak (pp. 116–118). O baseline atual usa um gold único "Dm" para essas músicas: o `detect_key` "acerta" pela razão errada (a Fase B v2 inverte para menor), e o relatório expõe `tonal_regions` com 21 fragmentos ruidosos para Wave (window=8). A medição não reflete a estrutura real e a apresentação é ilegível.

## What Changes

- `key_baseline.py`: dois registros do corpus ganham gold multi-região `(primary, [secondaries])` — Wave `("Dm", ["D"])` e Chega de Saudade `("Dm", ["D"])`; o script exibe as músicas modulantes com uma métrica distinta (acerto total / parcial / erro).
- `harmonic_analysis/validation/key_accuracy.py`: o harness ganha suporte a gold multi-região; nova função `evaluate_modulating_song` e novo campo `MultiKeyEval`; músicas monotonais não são afetadas.
- `harmonic_analysis/domain/key_detection.py`: nova função `dominant_regions(regions, n_chords, min_pct)` que pós-processa a saída de `segment_keys`, fundindo regiões menores que `min_pct` dos acordes totais com a vizinha mais compatível (mesma tonalidade adjacente ou menor número de regiões).
- `harmonic_analysis/services/analysis_service.py`: `tonal_regions` passa a usar `dominant_regions` sobre o resultado de `segment_keys`, produzindo 2–4 regiões legíveis em vez de dezenas de janelas brutas.

## Capabilities

### New Capabilities

*(nenhuma — melhoria de medição e apresentação de capabilities existentes)*

### Modified Capabilities

- `key-detection`: nova função `dominant_regions` adicionada ao módulo; `segment_keys` não muda.
- `key-accuracy-evaluation`: harness estendido para gold multi-região; métricas de acerto parcial/total para músicas modulantes.
- `analysis-reporting`: `tonal_regions` no resultado passa a refletir regiões dominantes pós-processadas, não janelas brutas de 8 acordes.

## Impact

- `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py` — adição de `dominant_regions`.
- `packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py` — uso de `dominant_regions` na seção `tonal_regions`.
- `packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py` — suporte a gold multi-região.
- `scripts/key_baseline.py` — formato de gold estendido e nova coluna de saída.
- Testes: novos casos unitários para `dominant_regions`; casos de regressão para `tonal_regions` via `analyze_song_data_structured`.
