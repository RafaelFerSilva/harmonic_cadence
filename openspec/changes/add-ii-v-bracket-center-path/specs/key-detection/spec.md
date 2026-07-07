## ADDED Requirements

### Requirement: ii-V bracket path corrects a V detected as tonic when both methods bracket the tonic

The analyzer SHALL provide a **fourth corrective path (Path D — ii-V bracket)** to the
functional-dominant quality gate, for the **ii-V vamp trap**: a piece whose main progression is a
`ii-V` where the Krumhansl-Schmuckler estimate lands on the **V** and the functional-center finder
(`chediak_functional_center`) lands on the **ii**, so **neither** method picks the tonic (the
**I**, the target of the V). Unlike Paths A/B/C (purely structural), Path D SHALL consult the
functional center — the only safe discriminator, because a purely structural rule regresses
established-correct detections (Chediak #7: no blind rule).

Path D SHALL override the K-S center `Y` with `X = (Y − 7) mod 12` when ALL of:
1. **The functional center is the ii of X.** `chediak_functional_center` returns a center rooted on
   `(X + 2) mod 12` and typed **minor** (the `ii` of X). Both methods are then pre-tonic of the same
   `X`: the K-S `Y` is the `V`, the functional center is the `ii` (Chediak pp.84-85: the `ii-V` is
   subdominant + dominant tension; the tonic is the `I`).
2. **X is cadenced at least twice.** There are **≥ 2** resolutions of a functional `V7`/`SubV7`
   (`Category.DOMINANT`, rooted a fifth above or a semitone above `X`) to `X`, scanning the whole
   piece (the bass of the following chord lands on `X`).
3. **X appears as a point of repose** at least once (`Category.MAJOR`/`Category.MINOR` rooted on
   `X`) — in these vamps the tonic often also appears dominant-colored (`I7`/`C9`), so the strict
   predominant-repose test of Paths B/C is relaxed; the bracket signature itself is specific enough.
4. **X differs from Y.**

Path D SHALL be tried after Paths A/B/C and the `_tritone_gate` (which do not fire on the trap:
`Y` rests occasionally as the wrong mode, and `X` is not the first chord — the vamp opens on the
`ii`). The functional center SHALL be consulted **lazily** (imported at call time) and only after the
cheap structural preconditions hold, to avoid coupling cost on the common path. Consulting the
functional center introduces **no recursion** (`chediak_functional_center` does not call
`detect_key`) and **no import cycle** (`functional_center` depends only on `cifra_core`).

Path D corrects the **detector** only; it SHALL NOT change the functional center, so a corrected
piece MAY still be counted as a center **divergence** (the functional finder still picks the `ii`).
The already-correct detections and the center-corroboration count MUST NOT regress: Path D fires
only on the bracket signature, verified by whole-corpus simulation to be exactly the three ii-V-trap
pieces.

#### Scenario: A ii-V vamp trap is corrected to the I when both methods bracket it

- **WHEN** the K-S center `Y` is the `V` of `X`, the functional center is the `ii` of `X` (rooted
  `X+2`, minor), there are ≥ 2 functional `V7`→`X` resolutions, and `X` appears as a repose
  (e.g. `bolinha-de-sabao`/`menina`: `Dm7 G7 → C`, K-S `Y = G`, functional `Dm`; `rio`:
  `Gm7 C7 → F`, K-S `Y = C`, functional `Gm`)
- **THEN** the detected center is corrected to `X` (Path D) — `C`, `C`, `F` respectively

#### Scenario: Path D does not fire when the methods do not bracket a common tonic

- **WHEN** the functional center is NOT the `ii` of `X = (Y − 7)` — e.g. the two methods agree
  (`ceu-e-mar`, `pouca-duracao`: agree), or the functional center is the flip target itself or an
  unrelated chord (`feitinha-pro-poeta`: functional `D`, not the `ii` of `G`; `chora-tua-tristeza`:
  detect `D` is correct and functional is `G`, not a bracket)
- **THEN** Path D does NOT fire and the K-S / within-band / A-B-C result stands (no regression)

#### Scenario: Path D corrects the detector without moving the corroboration count

- **WHEN** Path D corrects a trap piece (detector `Y → X`)
- **THEN** the functional center is unchanged (still the `ii`), so the piece MAY still be reported as
  a center divergence — Path D improves the detector's correctness, not the agreement count
