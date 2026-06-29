## 1. Trava (antes de tocar código)

- [x] 1.1 `make test` — registrar a contagem verde (referência: 349).
- [x] 1.2 Simulação read-only (feita): gatilho base (first==last==X, Y=IV de X) dispara em
  **1/60** (Aquele Abraço, X=E=gold); zero quebras. Guardas 3–5 satisfeitas (X7, X tríade,
  X em alt top-2). Sondagem: K-S A=0.8943 / E=0.7516; `B7` nunca →E.

## 2. Caminho de âncora I7-funk (key_detection.py)

- [x] 2.1 `_i7_funk_anchor_path(symbols, ks_best, ranked) -> Optional[Tuple[int, str]]`:
  computa `X = first_root`; retorna `(X_pc, mode_de_X)` só se as 5 guardas valerem:
  (1) `first_root == last_root == X`; (2) `Y == (X+5)%12` e `X != Y`; (3) algum acorde raiz
  `X` é dominante-7; (4) algum acorde raiz `X` é tríade maior (repouso); (5) `X` ∈ top-2 das
  alternativas (`ranked`). Senão `None`.
- [x] 2.2 Reusar os helpers existentes de qualidade de acorde (`_chord_infos`/`Category`) —
  não reintroduzir parser paralelo.
- [x] 2.3 No `detect_key`, após o `_tritone_gate` e antes da correção de modo paralelo,
  chamar o caminho; se retornar, aplicar `(best_tonic, best_mode)` e re-derivar `best_score`
  (como já feito para o gate).

## 3. Testes (test_tritone_gate.py)

- [x] 3.1 Miniatura I7-funk: sequência que abre/fecha em E, vamp `E7(9) A7(13)`, E como
  tríade E como E7(9), K-S pega A → `detect_key` corrige p/ **E maior**. (Calibrar a
  miniatura até o K-S de fato pegar A.)
- [x] 3.2 Guard: sem `first==last` (ex.: começa em A) → não dispara.
- [x] 3.3 Guard: X só como `X7` (pedal de V, sem tríade de repouso) → não dispara (guarda 4).
- [x] 3.4 Guard: `Y != (X+5)%12` → não dispara (guarda 2).
- [x] 3.5 Sanidade: uma peça correta (ex.: ii-V-I em C) não é tocada pelo novo caminho.

## 4. Quality gate + docs

- [x] 4.1 `make test` verde; `make lint` limpo.
- [x] 4.2 `scripts/key_baseline.py` ao vivo: **centro 19/19** (Aquele Abraço fechado);
  ganho líquido: exata 74→**76**, relativa 81→**83**; modo 86 / coleção 97 idênticos; zero regressão.
- [x] 4.3 `ROADMAP.md` e `AGENTS.md` (gate de âncora I7-funk; Aquele Abraço fechado;
  centro 19/19; nenhum buraco de centro restante).
- [x] 4.4 `openspec validate i7-funk-anchor-gate --strict` passa; pronto para `openspec archive`.
