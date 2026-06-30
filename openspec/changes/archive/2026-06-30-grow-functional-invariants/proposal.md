## Why

`scripts/songbook_baseline.py` hoje checa **um** invariante funcional transposição-invariante
("trítono real ⇒ função dominante", 62/62 sem defeito). A frente #6 quer crescer isso num **gate
de regressão** que protege a teoria destilada. Um probe ao vivo (n=62) sobre três famílias
candidatas do Chediak mediu o que está VERDE hoje:

- **Diminuto (XXI-XXII):** um `Category.DIMINISHED` nunca é `Emp`/`SD`/`T`/`Modal` — só `D`/`Dsec`
  (vii°7 = dominante rootless, p.90) ou `Dim` (auxiliar/descendente/passagem). **0 defeitos — VERDE.**
- **ii-V / `D2` (XIX):** um `D2` deveria ser seguido de um acorde com **função** dominante.
  **~168 incoerências** (70 `D2→SD`, 57 `D2→T`, 34 `D2→Emp`, 7 `Outro`) em 46/62 — o `D2` é
  atribuído pela **qualidade** do próximo acorde, não pela sua **função**. **NÃO é verde** (bug
  latente do motor).
- **Cadência (XXXII):** numa Perfeita (V→I), o V deveria ter função dominante e o I ser `T`.
  **10 incoerências** (9 `D→D2`, 1 `D→Dim`) — cadência×função discordam. **NÃO é verde.**

Um gate de regressão precisa nascer **verde** — senão é relatório de bug, não gate. Logo esta
change adiciona só o invariante **verde** (diminuto) e formaliza o de trítono; as incoerências do
`D2` e da cadência são registradas como fixes futuros, com os números do probe, para não se
perderem.

## What Changes

- **Invariante de diminuto** no `songbook_baseline.py`: por música, todo `Category.DIMINISHED`
  cujo `function_code` ∉ {`D`,`Dsec`,`Dim`} é um defeito. Reportado como o de trítono (defeitos
  por música; esperado 62/62 limpo).
- **Formaliza o invariante de trítono** já existente como parte explícita do gate funcional.
- **Saída** do baseline ganha uma linha de invariante de diminuto ao lado do trítono.
- **Registro dos achados** (ROADMAP/AGENTS): as duas incoerências viram changes de FIX
  enfileiradas — `fix-d2-over-attribution` (~168, o `D2` deve exigir alvo com função dominante) e
  `fix-cadence-function-coherence` (10, cadência×função) — com os números do probe.
- **NÃO-ESCOPO:** consertar o `D2` ou a cadência (fixes separados); tocar `detect_key`,
  `chediak_functional_center`, ou o motor de análise.

## Capabilities

### New Capabilities
<!-- nenhuma -->

### Modified Capabilities
- `functional-analysis-baseline`: o requisito "The baseline asserts Chediak functional
  invariants" fica **honesto sobre o que é gate verde**: os invariantes **duros** que o baseline
  asserta como defeitos são o **trítono** (real ⇒ dominante) e o **diminuto** (nunca
  Emp/SD/T/Modal); a **recognição** de ii-V e a **marcação** de cadências permanecem (o motor as
  produz), mas a **coerência** ii-V↔função e cadência↔função é declarada **adiada** (incoerências
  conhecidas, medidas, não gateadas) — não mais listada como invariante já válido.

## Impact

- **Código:** só `scripts/songbook_baseline.py` (+ docs `ROADMAP.md`/`AGENTS.md`). Nenhuma
  mudança no motor, em `detect_key` ou no achador funcional.
- **Gate:** re-rodar `scripts/songbook_baseline.py` — invariante de **diminuto 62/62** e
  **trítono 62/62**; a saída ganha a linha de diminuto. `make test` verde, `make lint` limpo.
- **Regra de ouro:** transposição-invariante, sobre `cifras/*.md`, nunca contra `cc_key`.
