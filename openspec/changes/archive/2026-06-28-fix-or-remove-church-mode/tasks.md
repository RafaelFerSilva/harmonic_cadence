## 1. Remover a promoção de detect_mode no pipeline (analysis_service.py)

- [x] 1.1 Remover a chamada `mode_info = detect_mode(...)`, o gate `_mode_refines_key` e a fusão modo→tonalidade (~333-342): `analysis` passa a ser sempre `HarmonicAnalysis(key, mode)` quando há `key`, senão `None`.
- [x] 1.2 Remover a função `_mode_refines_key` e a constante `MINOR_MODES` se ficarem sem uso após 1.1 (verificar com grep).
- [x] 1.3 Remover a seção `_modal` em `_add_depth_sections` (~436-463) e a chamada `_safe_section(result, "modal_analysis", _modal, None)`; ajustar a assinatura de `_add_depth_sections` para não receber/usar `mode_info`.
- [x] 1.4 Remover os imports agora órfãos em `analysis_service.py` (`detect_mode`, `modal_cadences`, `CHARACTERISTIC_NOTE`, `MODAL_CADENTIAL`, `MODAL_AVOID`) — manter só o que outras seções usam (verificar com ruff).

## 2. Remover o campo morto KeyEstimate.church_mode (key_detection.py)

- [x] 2.1 Remover o campo `church_mode: Optional[str] = None` do dataclass `KeyEstimate` (~55).
- [x] 2.2 Remover o preenchimento `info = detect_mode(...)` / `church_mode = ...` e o argumento passado ao construir o `KeyEstimate` (~233-236); remover o import de `detect_mode` em `key_detection.py` se ficar órfão.

## 3. Testes

- [x] 3.1 Remover `packages/harmonic_analysis/tests/test_key_mode.py` (exercita o campo morto).
- [x] 3.2 Rodar a suíte; ajustar `test_reports_sections.py` e `test_tier2_integration.py` se afirmarem a presença da seção modal ativa — a expectativa correta passa a ser **ausência/omção** da seção `modal_analysis` (a spec `analysis-reporting` já manda omitir quando `None`).
- [x] 3.3 Confirmar que `test_modal_corpus.py`, `test_modal_cadential.py`, `test_modal_field.py` e `test_pt_br_localization.py` (church_mode_pt) **continuam verdes** — a biblioteca modal é preservada.

## 4. Validação e ROADMAP

- [x] 4.1 Rodar `make test` (todos verdes) e `make lint`.
- [x] 4.2 `uv run python scripts/key_baseline.py` (rede): confirmar que as métricas modo/exata/relativa/coleção ficam **idênticas** ao baseline anterior (a change não toca detecção) — registrar a paridade.
- [x] 4.3 Sanidade no relatório: gerar a análise de uma das 12 músicas antes-falso-frígio (ex.: `uv run harmonic analyze "Tom Jobim" "Corcovado"`) e confirmar que **não** há mais seção "Análise modal"/"Centro modal".
- [x] 4.4 Atualizar `ROADMAP.md`: `fix-or-remove-church-mode` feito (remove a mentira ativa, preserva a biblioteca modal); Incremento 3b segue **bloqueado** mas agora **desbloqueável** — a detecção modal real é uma change futura que traz corpus modal MPB curado + discriminador modal↔tonal principiado.
