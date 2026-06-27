## 1. Confirmação pré-remoção (rede de segurança)

- [x] 1.1 Baseline verde: `make test` (218 testes) e `make lint` passam antes de qualquer remoção.
- [x] 1.2 Provar ausência de uso dinâmico dos símbolos-alvo: `grep -rn "getattr\|importlib\|__dict__\|globals()" packages/harmonic_analysis` e confirmar que nenhum resolve `extract_sequences`, `analyze_harmonic_flow`, `modal_analysis`, `CADENCE_PATTERNS`, `MAJOR_SCALE`, `MINOR_SCALE` ou `MODE_NAMES` por string.

## 2. Remoção do módulo órfão

- [x] 2.1 Deletar `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_analysis.py` por inteiro.
- [x] 2.2 `make test` + `make lint` verdes após a remoção.

## 3. Remoção de métodos sem caller

- [x] 3.1 Remover `HarmonicAnalysis.extract_sequences` de `domain/harmony.py`.
- [x] 3.2 Remover `HarmonicAnalysis.analyze_harmonic_flow` de `domain/harmony.py`.
- [x] 3.3 Remover o `from collections import Counter` redundante solto no meio da classe (`Counter` já importado no topo de `harmony.py`).
- [x] 3.4 `make test` + `make lint` verdes.

## 4. Remoção de constantes sem consumidor

- [x] 4.1 Remover de `domain/constants.py`: `CADENCE_PATTERNS`, `MAJOR_SCALE`, `MINOR_SCALE`, `MODE_NAMES`.
- [x] 4.2 Conferir que nenhum `import` em `harmony.py`/`modal.py`/demais módulos referencia os nomes removidos (ajustar listas de import se preciso).
- [x] 4.3 `make test` + `make lint` verdes.

## 5. Verificação final

- [x] 5.1 Suíte completa verde (218 testes) e `ruff` limpo — comportamento idêntico ao baseline.
- [x] 5.2 `grep` final confirma que nenhum dos símbolos removidos sobrevive em `packages/` ou `scripts/`.
- [x] 5.3 `openspec validate remove-dead-code` sem erros; pronto para `openspec archive`.
