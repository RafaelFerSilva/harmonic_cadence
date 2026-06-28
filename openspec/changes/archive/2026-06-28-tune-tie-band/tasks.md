## 1. Filtro de linhas de afinação (cifra_core)

- [x] 1.1 Adicionar `_AFIN_RE = re.compile(r"(afinac|drop\s+[a-g]|capotraste)", re.IGNORECASE)` em `packages/cifra_core/src/cifra_core/lines.py` e incluir o branch em `_is_noise`
- [x] 1.2 Adicionar cenário de teste em `packages/cifra_core/tests/test_core.py` (ou arquivo dedicado) cobrindo: linha `"Afinação Drop D: D A D G B E"` é filtrada; linha `"Capotraste na 2ª casa"` é filtrada; linha de acorde normal (`"Am7"`) não é afetada; idempotência mantida após a adição

## 2. Recalibração do TIE_BAND (harmonic_analysis)

- [x] 2.1 Alterar `TIE_BAND = 0.06` para `TIE_BAND = 0.10` em `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py`
- [x] 2.2 Atualizar o comentário acima da constante para refletir o novo valor e mencionar o caso Papel Marché como motivação da recalibração
- [x] 2.3 Verificar que `test_confident_ks_is_not_overridden` em `test_tonal_center_detection.py` continua passando (K-S confiante, fora da banda mesmo com 0.10)

## 3. Testes de regressão da suíte completa

- [x] 3.1 Rodar `make test` e confirmar que todos os 255+ testes passam sem regressão (inclui `test_key_corpus`, `test_tonal_center_detection`, `test_parallel_mode_correction`)
- [x] 3.2 Rodar `make lint` e corrigir eventuais avisos do ruff introduzidos pelas alterações

## 4. Validação do baseline com rede

- [x] 4.1 Rodar `uv run python scripts/key_baseline.py` (requer rede) e registrar os novos números de modo/tônica/relativa para n=60
- [x] 4.2 Confirmar que "Papel Marche" aparece como "exato" (C major) na saída do baseline
- [x] 4.3 Confirmar que nenhuma outra música regrediu de "exato" ou "relativo" para "ERRO"
- [x] 4.4 Atualizar `ROADMAP.md` com os novos números do baseline e registrar Papel Marché como caso resolvido por esta change
