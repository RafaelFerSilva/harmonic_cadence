# Tasks — grow-functional-invariants

> Crescer o gate de regressão funcional do `songbook_baseline.py` com o invariante VERDE de
> diminuto (XXI-XXII), formalizar o de trítono, e enfileirar as incoerências medidas (D2,
> cadência) como fixes futuros. Escopo: `scripts/songbook_baseline.py` + docs.

## 1. Trava de baseline (referência)

- [x] 1.1 Rodar `uv run python scripts/songbook_baseline.py` e registrar: invariante de trítono
      62/62. Confirmar (probe da sessão) que o invariante de diminuto dá 0 defeitos antes de
      gatear.

## 2. Invariante de diminuto no baseline

- [x] 2.1 Adicionar `_diminished_invariant(chords, analysis)` no molde de `_dominant_invariant`:
      por acorde, se `Chord(sym).get_category().value == "diminished"` e o `function_code` ∉
      {`D`,`Dsec`,`Dim`}, é defeito (Chediak XXI-XXII / p.90). Disjunto do invariante de trítono
      (que só olha `category=="dominant"`).
- [x] 2.2 Imprimir a linha "INVARIANTE diminuto (XXI-XXII): músicas sem defeito: N/N" ao lado da
      do trítono; listar defeitos por música se houver.

## 3. Gate ao vivo + zero-regressão

- [x] 3.1 Re-rodar `scripts/songbook_baseline.py`: invariante de **diminuto 62/62** e de
      **trítono 62/62** (sem regressão). A saída ganha a linha de diminuto.
- [x] 3.2 `make test` verde, `make lint` limpo (inclui ruff em `scripts/songbook_baseline.py`).

## 4. Registrar achados + docs

- [x] 4.1 ROADMAP/AGENTS: enfileirar `fix-d2-over-attribution` (~168 incoerências `D2`→não-
      dominante; o `D2` deve exigir alvo com FUNÇÃO dominante, não só qualidade — a-ra-like) e
      `fix-cadence-function-coherence` (10 incoerências cadência×função), com os números do probe.
- [x] 4.2 Atualizar AGENTS "Estado atual": o baseline funcional agora gateia **trítono +
      diminuto** (ambos 62/62); coerência ii-V/cadência adiada (medida, não gateada). #6
      parcialmente fechado. `openspec validate grow-functional-invariants --strict` passa.
