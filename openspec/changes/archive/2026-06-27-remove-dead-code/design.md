## Context

Uma varredura de débito técnico mapeou código morto e um módulo órfão duplicado
no pacote `harmonic_analysis`. O caso central é `domain/modal_analysis.py`: uma
cópia literal — `normalize_note`, `transpose_scale`, `build_harmonic_field`,
`describe_modal_borrowing` — da lógica que já vive em `domain/harmony.py`, sem
nenhum import no código-fonte. Os demais itens (`extract_sequences`,
`analyze_harmonic_flow`, e quatro constantes) também têm zero consumidores.

Esta é a primeira de duas changes de limpeza. Ela é deliberadamente **só
subtração**: prepara o terreno para a `finish-note-spelling` (a finalização da
migração de spelling de nota), que aposenta os símbolos ainda vivos
(`MODE_HARMONY`, `NOTE_REPLACEMENTS`, `normalize_note`, `guess_key`).

## Goals / Non-Goals

**Goals:**

- Remover código com **0 consumidores** verificados (src + tests + scripts).
- Eliminar o módulo órfão `modal_analysis.py` *antes* de a próxima change editar a
  versão viva em `harmony.py` — para ninguém editar a cópia errada.
- Manter a suíte (218 testes) verde e o `ruff` limpo, sem qualquer mudança de
  comportamento observável.

**Non-Goals:**

- **Não** tocar nada com consumidor vivo: `MODE_HARMONY`, `MODES`,
  `NOTE_REPLACEMENTS`, `normalize_note`, `guess_key`, o caminho sustenido-só de
  `CHROMATIC_NOTES`. Tudo isso é da change seguinte.
- **Não** refatorar a classe `HarmonicAnalysis` (ela encolhe como efeito colateral;
  um refactor dedicado é outro escopo).
- **Não** alterar nenhum requisito de nenhuma spec — não há delta de comportamento.

## Decisions

**1. Separar a limpeza da migração (duas changes, não uma).**
Remoção pura é risco ≈ 0 e mergeável na hora; a migração de spelling toca correção
harmônica e precisa de testes de caracterização. Misturá-las tornaria o review e o
rollback mais difíceis. Alternativa considerada (uma change só): rejeitada por
acoplar riscos diferentes.

**2. Verificação por prova de ausência de uso, não por intuição.**
Cada símbolo foi conferido com `grep` em `packages/` + `scripts/` (src **e**
tests), restando apenas a definição. A rede de segurança final é a suíte: se um
"morto" for usado por reflexão/`getattr`, um teste quebra. Alternativa (confiar na
leitura): rejeitada — explícito é melhor que implícito.

**3. Deleção sem substituição.**
Nenhum dos símbolos removidos tem substituto a criar: ou são órfãos, ou já são
cobertos por código vivo (a `describe_modal_borrowing` viva em `harmony.py` cobre o
que o órfão duplicava; o `modal_field()` derivado já cobre o campo modal).

## Risks / Trade-offs

- **[Uso dinâmico oculto** (`getattr`, import por string) **de um símbolo "morto"]**
  → Mitigação: rodar a suíte completa após cada remoção; `grep` adicional por
  referências dinâmicas (`getattr(...,"extract_sequences")` etc.) antes de deletar.
  Se algo quebrar, o símbolo não estava morto → reabrir a análise, não forçar.
- **[A próxima change depende do estado limpo]** → Mitigação: manter o escopo
  estritamente na lista verificada; não antecipar remoções da migração.
- **Trade-off:** duas changes pequenas em vez de uma — mais cerimônia de OpenSpec,
  porém review e rollback atômicos. Aceito de bom grado.
