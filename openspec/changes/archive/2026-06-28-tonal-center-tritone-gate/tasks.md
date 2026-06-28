## 1. Gate de qualidade (key_detection.py)

- [x] 1.1 `_chord_infos(symbols)`: (raiz_pc, baixo_pc, categoria) por acorde, via `chord_parse`.
- [x] 1.2 `_tritone_gate(symbols, ks_best)`: dispara só se o centro Y do K-S aparece EXCLUSIVAMENTE como `Category.DOMINANT` (se repousa uma vez → None).
- [x] 1.3 Resolução: algum Y7 resolve numa 5ª abaixo, X = (Y−7) mod 12 (baixo seguinte cai em X).
- [x] 1.4 Repouso do alvo: X aparece como `Category.MAJOR`/`MINOR` (ponto de descanso); senão aborta. Guard do blues embutido (sem repouso → None). dim7 inelegível (não é DOMINANT).

## 2. Integração no detect_key

- [x] 2.1 Após o desempate within-band (Fase B v1), chamar `_tritone_gate`; se retornar X ≠ palpite, sobrepor o centro (mantendo o shape do `KeyEstimate`); correção de modo paralelo segue depois.
- [x] 2.2 Conservadorismo: dentro da banda nada muda; o override só age quando o centro do K-S é inequivocamente um V.

## 3. Testes (offline sintético)

- [x] 3.1 `test_tritone_gate.py`: V-como-tônica corrigida (Dó7→Fámaj7 → Fá); tônica em repouso NÃO rebaixada; blues guard (I7-IV7-V7 → None); dim7 inelegível; centro do K-S ausente → None.
- [x] 3.2 Não-regressão: diatônico maior intacto; desempate relativo (E7→Am) intacto; tônica como maj7 mantida.

## 4. Validação ao vivo (a trava) e ROADMAP

- [x] 4.1 `make test` (300 verdes) e `make lint`.
- [x] 4.2 `uv run python scripts/key_baseline.py` (rede): modo/coleção **idênticos** (86/97); exata 67→**69%**, relativa 74→**76%**, centro 74→**79%** (Garota corrigida). **Zero regressão** — a trava passou.
- [x] 4.3 Atualizar `ROADMAP.md`: gate de qualidade feito (V-como-tônica); arbitragem modal de centro + métrica degree-relative registradas como `modal-center-arbitration` (próxima); dim7-como-dominante anotado como change futura.
