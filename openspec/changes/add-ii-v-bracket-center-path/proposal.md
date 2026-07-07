## Why

A adjudicação da worklist de centro (`adjudicate-center-worklist`) isolou a **armadilha do
ii-V** (`neither_ii_v`): 3 músicas (`bolinha-de-sabao`, `menina`, `rio`) onde a peça é um vamp
`ii-V` — o `detect_key` (K-S) pega o **V** e o achador funcional pega o **ii**, e **nenhum** pega
a tônica (o **I**, alvo do V). A simulação ao vivo (293 músicas) provou que **todo gate puramente
estrutural regride** (confirma o #7): "abre em ii-V" quebra `ceu-e-mar`/`pouca-duracao` (agree) e
`feitinha-pro-poeta` (detect-certo); "detect = V do funcional" quebra `chora-tua-tristeza` (detect
certo). O único discriminador seguro usa **os DOIS métodos**: quando o `detect_key` pegou o **V de
X** e o achador funcional pegou o **ii de X**, ambos são pré-tônica do MESMO X ⇒ X é a tônica
(Chediak pp.84-85: o ii-V é tensão SD+D, a tônica é o I). Medido: essa regra corrige **exatamente**
`bolinha`/`menina`/`rio` (→ Dó/Dó/Fá), **zero falso-positivo em 293**.

## What Changes

- **Novo Path D (bracket) no gate de qualidade do `detect_key`** (`domain/key_detection.py`):
  corrige `Y → X = (Y−7)` quando (1) o achador funcional (`chediak_functional_center`, **import
  tardio**) aponta o **ii de X** (raiz `X+2`, menor); (2) há **≥2** resoluções de `V7`/`SubV7` → X;
  (3) X aparece como repouso ao menos 1×; (4) X≠Y. É o **único** caminho que consulta o achador
  funcional (os A/B/C são puramente estruturais) — o preço da segurança contra o #7. Guardado por
  pré-condições baratas antes de computar o funcional (custo só quando a assinatura é plausível).
- **Correção, não placar.** O gate deixa o `detect_key` **correto** nos 3 casos, mas **NÃO** muda a
  corroboração 216/262: o achador funcional segue pegando o ii, então detect (agora o I) e funcional
  (o ii) ainda divergem. Subir o placar exigiria também corrigir o achador funcional — **fora deste
  escopo** (decisão registrada; seria um 2º subsistema do OURO). O corpus de adjudicação já registra
  o I citado para os 3; este gate alinha o detector à teoria.
- **Zero regressão provada** por simulação (só os 3 mudam) e re-verificada ao vivo
  (`songbook_baseline.py`): 3 gates duros 293/293, os 8 `detect`-certos e os 216 agree intactos.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `key-detection`: acrescenta o **Path D (bracket ii-V)** ao gate de qualidade que corrige um V
  detectado como tônica — o único path que consulta o centro funcional, para a armadilha ii-V onde
  os dois métodos cercam a tônica.

## Impact

- **Código:** `packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py` (nova
  função `_ii_v_bracket_path` + wiring no `detect_key`, após o `_tritone_gate`, antes do i7-funk);
  import tardio de `harmonic_analysis.validation.functional_center.chediak_functional_center`
  (sem ciclo: `functional_center` só depende de `cifra_core`, e não chama `detect_key` — sem
  recursão). Testes novos em `packages/harmonic_analysis/tests/`.
- **Invariantes:** 3 gates duros **293/293**; corroboração de centro **inalterada** (216/262 — ver
  acima); os 8 `detect`-certos e os 216 agree **não regridem** (provado por simulação). O gate é
  ultraconservador (só dispara na assinatura bracket).
- **Fora de escopo:** corrigir o achador funcional (mover o placar); os casos `V↔I` onde o funcional
  já acerta (ex. `me-perdoe-maria`) — geometria diferente, não é bracket.
