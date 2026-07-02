## Why

Ao implementar `persist-analysis-corpus` descobriu-se que **2 dos 4 gates do
`songbook_baseline.py` não executam**: `_dominant_invariant` e `_diminished_invariant`
chamam `Chord(sym).get_category()` e `tgt.bass`, que **não existem** na classe `Chord`
(`domain/chord.py` expõe `.quality`, `.root`, `.is_minor`, `.is_dominant_seventh`,
`.properties.bass` — não `get_category()`/`.bass`). As chamadas ficam dentro de
`try/except Exception: continue`, então toda iteração lança `AttributeError` e é pulada:
o "170/170 sem defeito" dos gates de **trítono** e **diminuto** é **vacuosamente verdadeiro**
— eles não checam nada.

Rodando a checagem correta (`.quality`, que funciona): **diminuto = 0** (invariante real,
seguro), mas **trítono = 944 flags em 155/170 músicas**, dominadas por `→T` (592; tônica `I7`
de blues/funk, legitimada pelo `i7-funk-anchor`) e `→Emp` (278; empréstimo modal). O
invariante "trítono real ⇒ dominante", como escrito, **não é limpo** — tem exceções que o
próprio projeto introduziu. Isso exige **adjudicação Chediak**, não um gate cego.

## What Changes

- **Corrigir o bug do baseline**: `_dominant_invariant`/`_diminished_invariant` passam a usar
  o acessor que existe (`Chord(sym).quality`), e `_d2_resolution_invariant` passa a usar
  `.properties.bass` — os gates voltam a **executar de fato**.
- **Diminuto vira gate executável verde** (0 violações) — endurece o baseline sem regressão.
- **Caracterizar e afiar o ledger de trítono** (não vira gate verde). A investigação recortou
  as 944 estruturalmente: **425** são `→T` grau **I** com root **== tônica** = **I7 como tônica**
  (blues/funk), classe legítima já documentada pelo projeto (`i7-funk-anchor`) — **isentável** de
  forma estrutural e transposição-invariante (grau `I` + função `T`). Os **~519** restantes
  (`→T` em VI/III = `T`-por-grau ignorando o trítono; `→Emp` backdoor/ambíguo; `→Outro`
  não-classificado) são **mistura de bug real e ambiguidade que exige adjudicação página-a-página
  do Chediak** — fora do escopo desta change (não se cita o que não se tem). Logo o trítono
  **permanece ledger de curadoria**, agora **afiado** (filtra os 425 legítimos, deixa ~519 como
  worklist honesta), tanto no `songbook_baseline.py` quanto na view `v_ledger_tritone_nondominant`.
- **Sincronizar a documentação**: AGENTS.md/ROADMAP hoje afirmam "170/170" para gates que não
  rodavam — corrigir a narrativa (diminuto vira gate verde real; trítono é ledger afiado ~519).

## Capabilities

### New Capabilities
<!-- Nenhuma capability nova: é correção de um invariante de validação existente. -->

### Modified Capabilities
- `functional-analysis-baseline`: os invariantes de trítono e diminuto passam a **executar**
  (hoje são no-ops); o de trítono é refinado com as exceções Chediak (I7 tônico, empréstimo
  modal) ou rebaixado a ledger. Muda o comportamento observável do baseline (gate real).

## Impact

- **Código:** `scripts/songbook_baseline.py` (acessores corrigidos + refino do invariante de
  trítono); possivelmente `domain/chord.py` (expor `get_category()`/`bass` se preferir manter a
  API que o baseline assumia). Sem impacto no motor de análise em si — é a camada de validação.
- **Corpus:** re-mede os 4 gates sobre `cifras/*.md` (n=170) com os gates realmente rodando.
- **Persistência:** a change `persist-analysis-corpus` já expõe `v_ledger_tritone_nondominant`
  como worklist desta adjudicação; ao fechar aqui, o refino pode virar um `v_gate_tritone`
  executável (com as exceções) na camada de persistência.
- **Precedência teórica:** toda decisão de exceção **cita a página do Chediak** (I7 tônico,
  empréstimo modal), coerente com "Chediak é o árbitro".
