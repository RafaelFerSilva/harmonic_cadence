## 1. dominant_regions (key_detection.py)

- [x] 1.1 Implementar `dominant_regions(regions: List[KeyRegion], n_chords: int, min_pct: float = 0.10) -> List[KeyRegion]` em `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py`: fundir regiões adjacentes de mesma tonalidade (tônica + modo iguais) e iterar removendo a menor região abaixo de `min_pct`, redirecionando seus acordes para a vizinha de mesma tonalidade ou (se não existir) para a vizinha com maior score K-S
- [x] 1.2 Exportar `dominant_regions` no `__init__` do módulo se necessário (verificar se outros módulos importam de `key_detection` diretamente)
- [x] 1.3 Adicionar testes em `packages/harmonic_analysis/tests/test_key_detection.py` (ou arquivo dedicado): peça single-key retorna 1 região; peça bimodal (Dm ↔ D major) retorna 2; regiões minúsculas são absorvidas; `segment_keys` sem `dominant_regions` continua produzindo as janelas brutas

## 2. Apresentação no analysis_service

- [x] 2.1 Em `packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py`, alterar a seção `tonal_regions` do `_safe_section` para chamar `dominant_regions(regions, len(all_chords))` em vez de expor `regions` diretamente
- [x] 2.2 Verificar que o formato de saída de cada entrada de `tonal_regions` (`start`, `end`, `key`, `score`) é preservado — `dominant_regions` devolve `KeyRegion`, mesma estrutura

## 3. Harness multi-região (key_accuracy.py)

- [x] 3.1 Em `packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py`, adicionar `dataclass MultiKeyEval` com campos `name`, `primary_gold`, `secondary_golds`, `detected_key`, `detected_regions`, `primary_ok`, `all_ok`
- [x] 3.2 Adicionar função `evaluate_modulating_song(name, chords, primary_gold, secondary_golds)` que chama `detect_key` + `dominant_regions(segment_keys(...))` e preenche `MultiKeyEval`
- [x] 3.3 Adicionar testes unitários para `evaluate_modulating_song` com corpus sintético (progressão bimodal conhecida)

## 4. Baseline multi-região (key_baseline.py)

- [x] 4.1 Alterar as entradas de Wave e Chega de Saudade em `GOLD` de `(artista, música, "Dm")` para `(artista, música, "Dm", ["D"])` (4 elementos = modulante)
- [x] 4.2 No `main()`, separar o processamento de entradas com 3 elementos (monotonais) e 4 elementos (modulantes); chamar `evaluate_modulating_song` para as modulantes
- [x] 4.3 Imprimir seção separada "Músicas modulantes" ao final do relatório, com colunas `primary_ok` / `all_ok`
- [x] 4.4 Garantir que as músicas modulantes NÃO entram no cálculo das métricas agregadas (modo %, tônica exata %, relativa-consciente %) — denominador = n_monotonais

## 5. Testes de regressão e validação

- [x] 5.1 Rodar `make test` — todos os testes devem passar; verificar em especial `test_reports_sections.py` e `test_integration_analysis.py` (que exercitam `tonal_regions`)
- [x] 5.2 Rodar `make lint`
- [x] 5.3 Rodar `uv run python scripts/key_baseline.py` (requer rede): verificar que Wave e Chega de Saudade aparecem na seção de modulantes, que os números monotonais não regridem, e documentar o resultado em `ROADMAP.md`
