## 1. Caracterização (test-first)

- [x] 1.1 Unit tests de `_correct_parallel_mode`: `["Cm","Fm","G7","Cm"]` em Dó
  inverte major→minor; `["C","F","G7","C"]` inverte minor→major; gate: tônica
  não-âncora (termina noutro tom) não inverte; voto fraco (um `i` isolado) não inverte.
- [x] 1.2 Integração: uma peça claramente menor lida em paralela maior é corrigida
  para menor; a Sina permanece **A maior** (acordes de tônica maiores → sem inversão).
- [x] 1.3 Invariante: `test_key_corpus` sintético continua 100%.

## 2. Correção de modo paralelo

- [x] 2.1 Implementar `_correct_parallel_mode(symbols, tonic_pc, mode)` em
  `domain/key_detection.py`: gate de âncora-baixo (último baixo == tônica OU cadência
  V/SubV → tônica nos últimos ~4) + voto de qualidade dos acordes de tônica
  (`+1` menor / `−1` maior); inverte se `|voto| >= PARALLEL_VOTE_THRESHOLD` (=2) e
  contradiz o modo. Limiar num bloco nomeado.
- [x] 2.2 Em `detect_key`, aplicar a correção após o desempate de banda; se o modo
  virar, atualizar o `score` para o do par corrigido. Preservar `alternatives`.

## 3. Medir e verificar

- [x] 3.1 Testes 1.1–1.3 verdes; suíte offline completa verde + ruff limpo.
- [x] 3.2 Rodar `scripts/key_baseline.py` (rede, n=60); registrar o ganho (esperado
  ~modo 83% / exata 62% / relativa 72%) e listar as músicas que viraram.
- [x] 3.3 Conferir que nenhuma música **correta** regrediu; documentar laterais
  (ex.: *Fotografia*).
- [x] 3.4 `openspec validate parallel-mode-correction` sem erros; pronto para archive.
