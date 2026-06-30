## Context

`scripts/songbook_baseline.py` já tem o arcabouço de invariante por música (`_dominant_invariant`
reporta defeitos do trítono, 62/62 limpo). O motor expõe, por acorde,
`result["harmonic_analysis"][i]["function_code"]`, e `cifra_core` dá a categoria do acorde
(`Chord(sym).get_category().value`). Um probe ao vivo (n=62) confirmou: o invariante de diminuto
está **verde** (0 defeitos); os invariantes de coerência ii-V (~168) e cadência (10) estão
**vermelhos** por incoerência real do motor (o `D2` casa pela qualidade do próximo acorde, não
pela função; a cadência casa por grau, não por código de função).

## Goals / Non-Goals

**Goals:**
- Somar o invariante de diminuto (verde) ao gate, no mesmo molde do trítono.
- Deixar o gate **sempre verde** (gate, não relatório de bug).
- Registrar as incoerências medidas (D2 ~168, cadência 10) como fixes enfileirados, com números.

**Non-Goals:**
- Consertar o `D2` ou a cadência (fixes separados — mexem em `harmony.py`).
- Tocar `detect_key`, `chediak_functional_center`, motor de análise.
- Adicionar invariantes vermelhos ao gate.

## Decisions

**D1 — Invariante de diminuto no molde do trítono, lendo `function_code` da saída do motor.**
Por música, para cada acorde `Category.DIMINISHED`, defeito sse `function_code ∉ {D, Dsec, Dim}`.
Reusa o loop que já zipa `items` com `chords`. *Alternativa rejeitada:* checar o subtipo textual
(auxiliar/descendente) — frágil (depende do texto PT-BR); o código `Dim` + a exclusão de
Emp/SD/T/Modal é o invariante robusto e transposição-invariante.

**D2 — Aceitação do trítono inclui `Dext` e `SubV` explicitamente.**
Ao formalizar, o conjunto dominante é {`D`,`D2`,`Dsec`,`Daux`,`Dext`,`SubV`} (o probe mostrou que
esquecer `Dext`/`SubV` gera falsos defeitos). Manter o casamento por substring atual já cobre
`D`/`D2`/`Dsec`/`Daux`/`Dext` (começam com "D") e `SubV`; revisar para não classificar `Dim`
como dominante (Dim começa com "D" mas é diminuto!) — o invariante de diminuto e o de trítono
são disjuntos por categoria do acorde, então não há conflito: o trítono só olha
`category=="dominant"`, o diminuto só `category=="diminished"`.

**D3 — Incoerências viram texto de ROADMAP, não código.**
Registrar `fix-d2-over-attribution` (~168; o `D2` deve exigir que o alvo tenha FUNÇÃO dominante,
não só qualidade) e `fix-cadence-function-coherence` (10; cadência×função) como changes futuras
com os números do probe. Não criar as changes agora (fora do escopo); só enfileirar.

## Risks / Trade-offs

- **[O casamento por substring confunde `Dim` com dominante]** (`"D" in "Dim"`) → Mitigação: o
  invariante de trítono só roda sobre acordes `category=="dominant"`; um diminuto tem
  `category=="diminished"` e nunca entra nesse ramo. Os dois invariantes são disjuntos por
  categoria. Adicionar teste que prova a disjunção.
- **[Um diminuto raro legítimo codado fora de {D,Dsec,Dim}]** → seria um defeito REAL (o ponto do
  gate). Hoje são 0; se aparecer ao crescer o corpus, é regressão a investigar — comportamento
  desejado.

## Migration Plan

1. Adicionar `_diminished_invariant(chords, analysis)` no `songbook_baseline.py` (molde do
   `_dominant_invariant`): defeito sse `category=="diminished"` e `function_code ∉ {D,Dsec,Dim}`.
2. Imprimir a linha do invariante de diminuto ao lado do trítono (defeitos por música).
3. **Gate ao vivo:** rodar o baseline — diminuto 62/62, trítono 62/62. `make test`/`make lint`.
4. ROADMAP/AGENTS: enfileirar os dois fixes com os números do probe; marcar #6 como
   parcialmente fechado (gate verde plantado).

## Open Questions

- Nenhuma bloqueante. (A ordem dos fixes futuros — D2 antes da cadência — é decisão da próxima
  sessão; o D2 tem maior volume e causa-raiz mais clara.)
