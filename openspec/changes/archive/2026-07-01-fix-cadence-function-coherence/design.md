## Context

`analyze_cadences` ([cadence.py:32]) classifica por grau: para cada par `(i, i+1)` calcula
`a = degree_base(degree_seq[i])`, `b = degree_base(degree_seq[i+1])`, e ramifica. O ramo
`a == "V" and b == "I"` emite **Perfeita** (ou **Imperfeita** se invertido) + **Autêntica** (se
precedido por IV/II). O coder de função (`analyze_function`, fonte única) já decidiu, em
paralelo, que o alvo é `D2`/`Dim` — mas a cadência nunca consulta essa decisão.

A incoerência é a tensão **grau × função**: o acorde é o grau-I (identidade vertical, relativa ao
tom) mas FUNCIONA como não-tônica (o que ele faz, horizontalmente — lança um ii-V adiante, ou
passa cromaticamente). Chediak resolve a ambiguidade pela função: a cadência é "combinação D e T"
(XXXII p.110); a resolução de um dominante num acorde que é ele mesmo um ii é "resolução direta"
(XXXIII p.111), não cadência.

Probe ao vivo (n=62) — as 5 incoerências (10 pares, alguns repetem):
`ah-se-eu-pudesse C7(9)→Fm7(D2)`, `ate-parece B7(b9)→Em7(D2)`, `avarandado E7(9)→A°(Dim)`,
`enquanto-a-tristeza-nao-vem G7(b9)→Cm7(D2)`, `so-tinha-de-ser-com-voce C7(b9)→Fm7(9)(D2)`.

## Goals / Non-Goals

**Goals:**
- A família autêntica/plagal só resolve na tônica quando o alvo FUNCIONA como repouso (T).
- Suprimir (não reclassificar) os pares de resolução direta — elos de cadeia não são cadências.
- Backward-compatible (param opcional); transposição-invariante (guarda por função, não por tom).
- Gatear a coerência no baseline — nasce verde.

**Non-Goals:**
- Mexer no coder de função (`D2`/`Dim` está correto), no `detect_key` ou no pré-passe do `D2`.
- Reclassificar o par como deceptiva (decisão D3) ou tocar meia-cadência/deceptiva.
- Detecção de tom das músicas em quarentena/worklist (#7, fora de escopo).

## Decisions

**D1 — `analyze_cadences` ganha `function_codes: Optional[Sequence[Optional[str]]] = None` (5º
param, alinhado por índice a `all_chords`/`degree_seq`).** Sem ele, comportamento idêntico ao
atual (grau-puro). *Alternativa rejeitada:* reordenar a saída detalhada e fazer a cadência lê-la
internamente — acopla a cadência ao formato do `harmonic_analysis`; passar a lista crua de
códigos é mais simples e testável.

**D2 — Guarda de repouso nos ramos que resolvem na tônica (`b == "I"`).** Helper
`_non_repose(code)`: `True` sse o código é uma função de tensão — `code.startswith("D")` (cobre
`D`, `D2`, `Dsec`, `Daux`, `Dext`, `Dim`) **ou** `code.startswith("Sub")` (cobre `SubV`, `Sub2`).
Nenhuma função de repouso começa com `D`/`Sub` (`T`, `SD`, `Emp`, `Modal`, `Blues`, `Outro`).
Quando `function_codes` está presente e o alvo `i+1` é não-repouso, os ramos Perfeita/Imperfeita/
Autêntica/Plagal **não classificam** o par. *Alternativa rejeitada:* exigir o alvo `== "T"`
exatamente — removeria cadências modais legítimas (alvo `Modal`); a guarda mira só a tensão
medida (dominante/diminuto), conservadora.

**D3 — Suprimir, não reclassificar como deceptiva.** A deceptiva é punctuação de frase ("o
dominante seguido por grau que não é a tônica", XXXII p.110). Os pares aqui são elos internos de
uma cadeia de ii-V/dominantes secundários (XXXIII *resolução direta*) — não há evento cadencial.
Rotulá-los "deceptiva" super-atribuiria uma cadência onde há só uma cadeia, e produziria o
relatório contraditório "V→I deceptiva". Suprimir é a leitura honesta. *(O alvo segue codado
`D2`/`Dim` no `harmonic_analysis` — a função não muda, só a cadência deixa de mentir.)*

**D4 — A guarda vale para todos os ramos `b == "I"` (autêntica + plagal), não só `a == "V"`.**
Mantém o invariante de coerência **total**: nenhuma cadência que afirma resolução na tônica tem
alvo de função não-repouso. No corpus atual só a família autêntica dispara, mas a plagal recebe a
mesma guarda por princípio (regra nasce coerente, não só verde).

**D5 — Call site: construir `_detailed_harmonic_analysis` ANTES da cadência.** Hoje a saída
detalhada (com `function_code`) é montada na linha 363, **depois** da cadência (351). Mover para
antes e extrair `[it["function_code"] for it in harmonic_analysis]` para passar a
`analyze_cadences`. O `formatter.py` (outro consumidor) já monta a análise antes de formatar — sem
regressão. Fonte única de função preservada.

## Risks / Trade-offs

- **[Remover uma cadência legítima]** se o coder errasse um `T` para `D2`/`Dim`. → Mitigação: o
  coder de função é a autoridade já gateada (invariante trítono/diminuto 62/62); um alvo codado
  `D2`/`Dim` É, por construção, não-repouso. A guarda só remove o que o motor já chama de tensão.
- **[Par de resolução direta fica "sem cadência" no relatório]** → CORRETO: Chediak XXXIII não
  chama isso de cadência. O relatório mostra a função (`D2`/`Dim`) no acorde; a ausência de
  cadência é honesta, não uma lacuna.
- **[Backward-compat dos testes da taxonomia]** os testes chamam `analyze_cadences` sem
  `function_codes` → guarda inativa → verdes. Novos testes cobrem a guarda ativa.

## Migration Plan

1. `cadence.py`: novo param `function_codes` + helper `_non_repose` + guarda nos ramos `b == "I"`.
2. `analysis_service.py`: mover `_detailed_harmonic_analysis` para antes da cadência; extrair os
   `function_code`s e passar a `analyze_cadences`.
3. Testes unitários: alvo `D2`/`Dim` ⇒ par NÃO vira Perfeita/Autêntica/Imperfeita/Plagal; alvo
   `T` ⇒ cadência normal (regressão); sem `function_codes` ⇒ grau-puro (backward-compat).
4. `songbook_baseline.py`: gate de coerência de cadência (alvo autêntico/plagal nunca
   dominante/diminuto) — nasce 62/62 verde; provar dentes + não-vácuo (há cadências reais).
5. **Gate ao vivo:** re-rodar o probe — 5 incoerências → 0; `songbook_baseline.py` trítono/
   diminuto/D2 **62/62**; coerência de cadência **62/62**; `make test`/`make lint`.

## Open Questions

- Nenhuma bloqueante. (A taxonomia das 5 cadências como métrica de cobertura no baseline — a "3ª
  família" do #6 — é reconhecimento já produzido; esta change fecha a **coerência**, que era o que
  faltava.)
