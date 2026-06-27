## Why

A varredura de débito técnico encontrou código morto e um módulo órfão duplicado
convivendo com o código vivo. O pior ofensor — `domain/modal_analysis.py` — é uma
cópia literal da lógica de empréstimo modal de `domain/harmony.py`, sem nenhum
import: um atrator de confusão (alguém vai editar a cópia errada). Limpar o
terreno **antes** de finalizar a migração de spelling de nota evita editar a
duplicata e reduz o ruído para enxergar as costuras reais.

## What Changes

Pura subtração — nada é substituído, nenhum comportamento observável muda. Cada
item foi verificado como tendo **0 referências** em `packages/` e `scripts/`
(src + tests), sobrando apenas a própria definição:

- Deletar o módulo órfão `domain/modal_analysis.py` por inteiro (0 imports; os
  matches de "modal_analysis" no código são a chave de resultado `"modal_analysis"`,
  não o módulo). Duplica `describe_modal_borrowing`/`_transpose_scale`/
  `normalize_note`/`build_harmonic_field` já existentes em `domain/harmony.py`.
- Remover `HarmonicAnalysis.extract_sequences` (`harmony.py`) — 0 callers.
- Remover `HarmonicAnalysis.analyze_harmonic_flow` (`harmony.py`) — 0 callers.
- Remover de `domain/constants.py` as constantes sem consumidor: `CADENCE_PATTERNS`,
  `MAJOR_SCALE`, `MINOR_SCALE`, `MODE_NAMES`.
- Remover o `from collections import Counter` redundante solto no meio da classe
  em `harmony.py` (`Counter` já é importado no topo do arquivo).

**Fora de escopo** (ainda têm consumidores; serão aposentados na change seguinte
`finish-note-spelling`): `MODE_HARMONY`, `MODES`, `NOTE_REPLACEMENTS`,
`normalize_note`, `guess_key`, e o caminho sustenido-só de `CHROMATIC_NOTES`.

## Capabilities

### New Capabilities

Nenhuma. Esta change não introduz comportamento.

### Modified Capabilities

- `modal-tonal-center`: ganha um requisito **estrutural** de fonte única — o campo
  modal e a descrição de empréstimo modal têm implementação única; nenhum módulo
  órfão duplica as rotinas a partir das tabelas legadas. É garantia de manutenção,
  **sem mudança de comportamento observável**: o campo modal derivado e as
  descrições permanecem idênticos.

Nenhuma outra capability muda. Toda saída observável (`key-detection`,
`harmonic-function`, `analysis-reporting`, etc.) permanece idêntica em
comportamento e contrato.

## Impact

- **Código:** `packages/harmonic_analysis/src/harmonic_analysis/domain/` —
  `modal_analysis.py` (removido), `harmony.py`, `constants.py`.
- **Testes:** nenhum teste referencia os símbolos removidos (verificado). A própria
  suíte é a rede de segurança: 218 testes verdes antes e depois.
- **APIs/contratos:** nenhum. JSON/Markdown/HTML de saída inalterados.
- **Risco:** ≈ 0. Se a remoção quebrar algum teste, isso prova que o símbolo
  **não** estava morto → reabrir a análise em vez de forçar a remoção.
