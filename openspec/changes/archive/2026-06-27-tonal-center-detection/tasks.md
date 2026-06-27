## 1. Rede de caracterização (test-first)

- [x] 1.1 Baseline: `make test` verde e baseline de rede registrado (modo 64% /
  exata 46% / relativa 61%, n=28) antes de mexer.
- [x] 1.2 Teste-invariante (offline): `test_key_corpus` sintético continua 100% — o
  desempate NÃO pode regredir progressões diatônicas claras.
- [x] 1.3 Testes-alvo (offline, com as progressões reais reduzidas a símbolos):
  uma progressão relativa que termina `G7→C` detecta **C maior** (não A menor); uma
  que termina `E7→Am` detecta **A menor**.
- [x] 1.4 Teste de não-override: numa progressão onde um tom vence o K-S fora da
  banda, o resultado é idêntico ao K-S puro.

## 2. Corroboração cadencial

- [x] 2.1 Implementar `cadence_corroboration(symbols, tonic_pc, mode) -> float` em
  `domain/key_detection.py`: +1 (1º acorde=tônica), +2 (último=tônica) ±1 (qualidade
  casa/contraria o modo), +3 (cadência autêntica dominante→tônica nos últimos ~4).
  Pesos num bloco nomeado, recalibráveis.
- [x] 2.2 Em `detect_key`, após o ranking K-S, re-rankear **só** os candidatos com
  `score >= top - EPS` por corroboração (desempate por score K-S). EPS conservador
  (~0.05–0.08) numa constante documentada; fora da banda, K-S prevalece.
- [x] 2.3 Preservar a forma do `KeyEstimate` (best + `alternatives` do ranking K-S).

## 3. Medir e verificar

- [x] 3.1 Testes 1.2–1.4 verdes; suíte offline completa verde + ruff limpo.
- [x] 3.2 Rodar `uv run python scripts/key_baseline.py` (rede); registrar o ganho
  in-sample (esperado ~modo 71% / exata 54%) e listar quais músicas viraram.
- [x] 3.3 Conferir que nenhuma música **correta** no baseline regrediu; se houver,
  ajustar EPS/pesos de forma principiada (não para casar o n=28) ou documentar.
- [x] 3.4 `openspec validate tonal-center-detection` sem erros; pronto para archive.

## 4. Registrar limites e follow-ups

- [x] 4.1 Documentar (no design/handoff) que o ganho é in-sample e que a validação
  real é a ampliação do corpus.
- [x] 4.2 Registrar os follow-ups não resolvidos: override agressivo (Valsinha),
  segmentação de modulação real (Wave/Chega), tônica de modos.
