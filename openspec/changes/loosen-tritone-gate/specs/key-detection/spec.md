## MODIFIED Requirements

### Requirement: Functional-dominant quality gate corrects a V detected as tonic

When the Krumhansl-Schmuckler estimate centers on a chord that is actually the **dominant**, the analyzer SHALL be able to correct the center beyond the near-tie band — but ONLY via a conservative discriminator grounded in functional harmony (Chediak): the **tonic is a point of repose** (it appears as a stable chord — major/minor triad or `maj7`/`6`/`m7`), whereas the **dominant is tension** (it appears as a dominant seventh, carrying the tritone). A center can only be corrected when the evidence is unambiguous, so the established correct detections do not regress.

The gate SHALL override the K-S center `Y` with `X = (Y − 7) mod 12` (a perfect fifth below) via **either** of two paths:

**Path A — exclusive-dominant (restrictive).** ALL of:
1. **Y appears exclusively as a dominant seventh.** Every chord rooted on `Y` is typed `Category.DOMINANT`; if `Y` ever appears as a stable chord, it rests and IS a legitimate tonic.
2. **Y resolves down a fifth.** Some `Y7` resolves so the bass of the following chord lands on `X`.
3. **X is a point of repose.** `X` appears as a stable chord (`Category.MAJOR` or `Category.MINOR`).

**Path B — anchored-resolution (loosened).** When `Y` rests only occasionally (so Path A aborts), the gate MAY still correct `Y → X` when ALL of:
1. **A functional dominant resolves to X structurally.** A functional `V7`/`SubV7` (a real tritone, `Category.DOMINANT`) resolves to `X` in a structural/final position — the same criterion as `verify_tonal_center`.
2. **X is the predominant point of repose.** Chords rooted on `X` are predominantly stable (the `Category.MAJOR`/`Category.MINOR` count on `X` strictly exceeds its `Category.DOMINANT` count and is at least 2).
3. **X is a structural anchor.** `X` is the root of the **first** chord of the piece. Only the first chord (not the last): the piece establishes its tonic at the opening (as the cadential corroboration already weights), whereas the last chord can mislead — a piece whose tonic is `F` may close on its relative `D minor`, and anchoring on the last chord would make the gate flip the mode (a regression).
4. **X differs from Y.**

Path B exists because in dense-secondary-dominant MPB a true tonic's dominant (`Y`) is frequently re-used as a passing chord, so `Y` may itself appear once or twice as a stable chord even though it is functionally the V — Path A's "exclusively dominant" test then aborts and the V-as-tonic error survives. Path B keys off the **resolution target** `X` (anchored repose reached by a functional dominant) rather than the purity of `Y`, which is the robust functional signal.

The gate considers only `Category.DOMINANT` chords; a fully-diminished seventh is ineligible (it carries two tritones and no single resolution). Under BOTH paths, if `X` never appears as a stable chord (e.g. a `C7 F7 G7` blues where the target is also only a dominant), the gate aborts and the K-S / within-band result stands. The returned estimate keeps the same shape, and the four Cifra-Club baseline metrics for already-correct detections MUST NOT regress.

#### Scenario: A dominant detected as tonic is corrected to its resolution target
- **WHEN** the K-S center `Y` appears only as a dominant seventh (e.g. always `C7`, never `C`/`Cmaj7`), that `C7` resolves down a fifth to `F`, and `F` appears as a stable chord (e.g. `Fmaj7`)
- **THEN** the detected center is corrected to `F` (Path A)
- **AND** this holds even though `F` was outside the near-tie band

#### Scenario: A V that also rests occasionally is corrected via the anchored path
- **WHEN** the K-S center `Y` is predominantly a dominant but appears as a stable chord a few times, AND a functional `V7`/`SubV7` resolves to `X = (Y − 7) mod 12` in a final cadence, AND `X` is the predominant point of repose, AND `X` is the first chord of the piece
- **THEN** the detected center is corrected to `X` (Path B), even though `Y` is not exclusively a dominant
- **AND** this is the case for A Banda (A→D), Apesar de Você (A→D), and Menino do Rio (C→F)

#### Scenario: A resting tonic with no anchored functional dominant is never demoted
- **WHEN** the K-S center appears as a stable chord and no functional dominant resolves to an anchored predominant-repose `X`
- **THEN** neither path fires and the K-S center is kept
- **AND** the four Cifra-Club baseline metrics are unchanged

#### Scenario: A blues/mixolydian I7 is not demoted
- **WHEN** the tonic is a constant dominant seventh (e.g. a `C7 F7 G7` blues) so the resolution target also appears only as a dominant, with no stable point of repose
- **THEN** both paths abort and the dominant-quality tonic is kept (the blues/mixolydian character is handled as coloring, not as a functional dominant)

#### Scenario: A piece that closes on its relative is not flipped by the anchored path
- **WHEN** the real tonic opens the piece (e.g. `F`) but the piece closes on its relative minor (`D minor = (Y − 7)` for a detected `Y = A`), with that relative resting predominantly and reached by a functional dominant
- **THEN** Path B does NOT fire, because the anchor is the **first** chord (the real tonic `F`), not the last — so the detected mode is not flipped to the relative (no regression)

#### Scenario: A tonic that is itself an I7 is not corrected by the anchored path
- **WHEN** the real tonic appears predominantly as a dominant (an `I7` funk tonic) and the detected impostor is its subdominant, so no anchored predominant-repose target a fifth below the detection is reached by a functional dominant
- **THEN** Path B does not fire (the case is out of scope and the detection is left unchanged, not worsened)

#### Scenario: A diminished seventh never triggers the gate
- **WHEN** the only tritone-bearing chord on the candidate is a fully-diminished seventh
- **THEN** the gate does not fire (the dim7 is ineligible)

#### Scenario: No qualifying dominant leaves K-S unchanged
- **WHEN** the K-S center is not exposed as a dominant resolving to a resting target under either path
- **THEN** the detected key equals the K-S / within-band corroboration result
