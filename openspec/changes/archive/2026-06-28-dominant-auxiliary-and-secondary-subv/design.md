## Context

O ramo `if chord.is_dominant_seventh:` em `analyze_function` ([harmony.py:113](packages/harmonic_analysis/src/harmonic_analysis/domain/harmony.py#L113)) hoje, em ordem: (a) função especial por posição — `I7`(pos0)→T blues, `IV7`(pos5)→SD blues, `bVII7`(pos10)→Emp, `bVI7`(pos8)→Emp; (b) `V7/x` secundário (`ni==5`, alvo não-tônica); (c) `VII7` cadencial; (d) `SubV` primário (`bII7`, ½t acima da tônica). Os passos (a) **retornam antes** de checar a resolução, então `Bb7→Eb` (auxiliar) é capturado como `Emp bVII7` e `Ab7→G` (SubV7/V) como `Emp bVI7`. O `SubV` secundário e o dominante auxiliar simplesmente não existem.

A teoria foi lida do livro (scan, offset 0) e destilada: Chediak XVIII (p.99) — secundário = alvo **diatônico**; auxiliar = alvo de **empréstimo modal**; SubV7 secundário = ½t acima de um **diatônico**. A change é camada de função (não toca `detect_key`), então o baseline fica idêntico; a trava é a suíte.

## Goals / Non-Goals

**Goals:**
- Dominante **auxiliar** (`V7/<grau cromático>`, alvo de empréstimo modal, 5ª descendente).
- **SubV7 secundário** (`SubV7/<grau>`, alvo diatônico não-tônica, ½t descendente).
- Preservar: V7/x secundário, SubV primário, I7/IV7 blues, `bVII7`/`bVI7` que **não** resolvem.

**Non-Goals:**
- II cadencial secundário/auxiliar (Chediak XIX) — próxima change.
- Dominantes/II-V's estendidos, cadeias (XXVIII) — change futura.
- `roman.py` para os novos rótulos — fora do escopo (a função carrega a glosa).

## Decisions

### D1 — Nova ordem do ramo de dominante: blues → resolução → empréstimo-sem-resolução

A precedência correta (fiel ao Chediak) é:
1. **I7/IV7 blues** (pos 0/5) — Chediak XXXIV os fixa; **antes** de tudo (intocados).
2. **Resolução funcional** (com `next_chord`): **SubV7 secundário** (½t acima de diatônico não-tônica) e **dominante auxiliar** (5ª abaixo de alvo de empréstimo). Vêm **antes** dos `bVII7`/`bVI7`-Emp, para que `Bb7→Eb` e `Ab7→G` sejam lidos pela resolução.
3. **`bVII7`/`bVI7` Emp** (pos 10/8) — só alcançado quando NÃO houve resolução (ex.: `Bb7→C`).
4. **V7/x secundário** (`ni==5`, alvo diatônico não-tônica), **VII7 cadencial**, **SubV primário** — como hoje.

*Por quê essa ordem:* a função especial (XXXIV) tem precedência só para I7/IV7 (blues genuíno); para bVII7/bVI7 a **resolução** decide (XVIII-b vs XXXIV). Validado mentalmente contra os testes existentes (E7→Am, D7→G, Db7→C, G7→C, C7→G) — todos preservados.

### D2 — Distinção secundário vs auxiliar pelo `get_degree` do alvo

`target_degree = get_degree(next_chord)`: se **não-None** (diatônico) e não-tônica → secundário; se **None** (não-diatônico) e não-tônica → o alvo é empréstimo modal → **auxiliar**. *Por quê:* é exatamente o critério do Chediak (alvo diatônico vs empréstimo), e `get_degree` já é a fonte única de "diatônico ou não".

### D3 — Código `Daux` novo; `SubV` reusado para o secundário

Adicionar `Daux` ao `FunctionCode` e a `HARMONIC_FUNCTIONS` (o auxiliar é uma função distinta no Chediak, e o front vai exibi-la). O SubV7 secundário reusa o código `SubV` com nome `SubV7 secundário (SubV7/x)` — continua sendo um SubV. O grau cromático do alvo auxiliar (bIII/bVI/bVII) é nomeado por um helper `_chromatic_degree(target_root)` (offset→grau com bemol), para o rótulo `V7/bIII`.

### D4 — SubV7 de empréstimo fica fora

Chediak nota que "o SubV7 de um acorde de empréstimo modal é ouvido como V7 (secundário) de um grau diatônico" — ou seja, não há um "SubV auxiliar" próprio; ele colapsa no V7 secundário. Então não criamos rótulo para isso; o caso é coberto pela leitura de dominante secundário existente. *Mantém o escopo enxuto.*

## Risks / Trade-offs

- **[Reordenar o ramo regride um caso]** → a trava é a suíte (test_applied_dominants cobre E7→Am, D7→G, Db7→C, G7→C, C7→G; preservados por construção). Adiciono testes para os novos e re-rodo tudo.
- **[Alvo não-diatônico que não é empréstimo modal (modulação/cadeia estendida)]** → lido como auxiliar; aceitável por ora (as cadeias estendidas são a change XXVIII). O caso comum (V7/bIII, V7/bVI) é o alvo desta change.
- **[`Daux` novo quebra consumidores do enum]** → os códigos são usados como strings livres (sem validação de conjunto fechado); verifico `analyze_function_stats`/reharmonization não assumirem um conjunto fixo.
- **[Baseline]** → impossível regredir (`detect_key` intacto); rodo como sanidade.

## Migration Plan

1. Adicionar `Daux` em `constants.py`; helper `_chromatic_degree`.
2. Reordenar o ramo de dominante (blues → resolução [SubV2/Daux] → Emp → secundário/SubV primário).
3. Testes: auxiliar (`Bb7→Eb`, `Eb7→Ab`), SubV2 (`Ab7→G`, `Eb7→Dm`), e os invariantes (secundário, SubV primário, blues, bVII7→C).
4. `make test` + `make lint`; `scripts/key_baseline.py` ao vivo (idêntico). Atualizar ROADMAP. Rollback = restaurar a ordem anterior do ramo.

## Open Questions

- O grau cromático do alvo auxiliar (`bIII` vs `#II` etc.) usa bemóis por convenção (empréstimo modal grafa bemol). Suficiente para o rótulo; enarmonia fina fica fora.
