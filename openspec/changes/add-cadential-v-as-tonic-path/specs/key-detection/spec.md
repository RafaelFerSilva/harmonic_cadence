## MODIFIED Requirements

### Requirement: Functional-dominant quality gate corrects a V detected as tonic

When the Krumhansl-Schmuckler estimate centers on a chord that is actually the **dominant**, the analyzer SHALL be able to correct the center beyond the near-tie band — but ONLY via a conservative discriminator grounded in functional harmony (Chediak): the **tonic is a point of repose** (it appears as a stable chord — major/minor triad or `maj7`/`6`/`m7`), whereas the **dominant is tension** (it appears as a dominant seventh, carrying the tritone). A center can only be corrected when the evidence is unambiguous, so the established correct detections do not regress.

The gate SHALL override the K-S center `Y` with `X = (Y − 7) mod 12` (a perfect fifth below) via **any** of three paths, tried in order (A, then B, then C); the first that matches wins.

**Path A — exclusive-dominant (restrictive).** ALL of:
1. **Y appears exclusively as a dominant seventh.** Every chord rooted on `Y` is typed `Category.DOMINANT`; if `Y` ever appears as a stable chord, it rests and IS a legitimate tonic.
2. **Y resolves down a fifth.** Some `Y7` resolves so the bass of the following chord lands on `X`.
3. **X is a point of repose.** `X` appears as a stable chord (`Category.MAJOR` or `Category.MINOR`).

**Path B — anchored-resolution (loosened).** When `Y` rests only occasionally (so Path A aborts), the gate MAY still correct `Y → X` when ALL of:
1. **A functional dominant resolves to X structurally.** A functional `V7`/`SubV7` (a real tritone, `Category.DOMINANT`) resolves to `X` in a structural/final position — the same criterion as `verify_tonal_center`.
2. **X is the predominant point of repose.** Chords rooted on `X` are predominantly stable (the `Category.MAJOR`/`Category.MINOR` count on `X` strictly exceeds its `Category.DOMINANT` count and is at least 2).
3. **X is a structural anchor.** `X` is the root of the **first** chord of the piece.
4. **X differs from Y.**

**Path C — cadential-opening (whole-piece).** When the `V→I` cadence sits at the **opening** (not in the final window, so Path B's final-window resolution test misses it), the gate MAY correct `Y → X` when ALL of:
1. **X is cadenced at least twice.** There are **≥ 2** resolutions of a functional `V7`/`SubV7` (`Category.DOMINANT`, rooted a fifth above or a semitone above `X`) to `X` (the following chord's bass lands on `X`), scanning the **whole piece**. Repetition confirms `X` as the tonic rather than a one-off tonicization of the subdominant `IV`/`iv`.
2. **X is the predominant point of repose** (same as Path B: stable-count on `X` exceeds its dominant-count and is at least 2).
3. **X is the first chord** of the piece (the opening establishes the tonic).
4. **The piece does NOT end on `Y` as a point of repose.** If the last parseable chord is rooted on `Y` and is `Category.MAJOR`/`Category.MINOR`, then `Y` is confirmed as the tonic by the final structural repose (Chediak) and the gate aborts — this distinguishes a true `V`-as-tonic (which opens on `X` and does not rest on `Y` at the close) from a piece that opens on its `IV` but closes on the real tonic `Y` (a `V→IV` tonicization or blues `I7→IV`, locally identical to `V→I`).
5. **X differs from Y.**

Path C exists because a piece can state its `ii-V-I` (or `V-I`) at the opening and then move on, so the structural cadence is early, not final; Path B's final-window test then misses it. Path C keys off a **repeated** resolution to an opening-anchored `X` while refusing to fire when `Y` itself rests at the final structural position — the two structural anchors (first chord is `X`, last repose is not `Y`) together separate `V`-as-tonic from open-on-`IV`.

The gate considers only `Category.DOMINANT` chords; a fully-diminished seventh is ineligible (it carries two tritones and no single resolution). Under ALL paths, if `X` never appears as a stable chord (e.g. a `C7 F7 G7` blues where the target is also only a dominant), the gate aborts and the K-S / within-band result stands. Paths A and B are unchanged by the addition of Path C. The returned estimate keeps the same shape, and already-correct detections MUST NOT regress.

#### Scenario: A dominant detected as tonic is corrected to its resolution target
- **WHEN** the K-S center `Y` appears only as a dominant seventh (e.g. always `C7`, never `C`/`Cmaj7`), that `C7` resolves down a fifth to `F`, and `F` appears as a stable chord (e.g. `Fmaj7`)
- **THEN** the detected center is corrected to `F` (Path A)
- **AND** this holds even though `F` was outside the near-tie band

#### Scenario: A V that also rests occasionally is corrected via the anchored path
- **WHEN** the K-S center `Y` is predominantly a dominant but appears as a stable chord a few times, AND a functional `V7`/`SubV7` resolves to `X = (Y − 7) mod 12` in a final cadence, AND `X` is the predominant point of repose, AND `X` is the first chord of the piece
- **THEN** the detected center is corrected to `X` (Path B), even though `Y` is not exclusively a dominant
- **AND** this is the case for A Banda (A→D), Apesar de Você (A→D), and Menino do Rio (C→F)

#### Scenario: A V-as-tonic cadenced at the opening is corrected via the cadential path
- **WHEN** the piece opens with a `ii-V-I` (or `V-I`) to `X` that repeats (≥ 2 functional dominant resolutions to `X` over the whole piece), `X` is the predominant repose and the first chord, and the piece does NOT close on `Y` as a stable chord (e.g. `C7M Am7 Dm7 G7 C7M …` with K-S `Y = G`)
- **THEN** the detected center is corrected to `X` (Path C), even though the cadence is not in the final window
- **AND** this is the case for a-volta (G→C) and dia-de-vitoria (E→A)

#### Scenario: A one-off tonicization of the subdominant is not corrected
- **WHEN** the piece opens on its `IV`/`iv` and a functional dominant resolves to that opening chord only **once** (a passing tonicization), with the real tonic stated elsewhere
- **THEN** Path C does NOT fire (fewer than two resolutions to `X`), and the K-S center is kept

#### Scenario: A piece that opens on IV but closes on the real tonic is not corrected
- **WHEN** the piece opens on `X` (its `IV`) with two-or-more `V→X` resolutions, but the last chord rests on `Y` (the real tonic, e.g. `D` major at the close)
- **THEN** Path C does NOT fire (the final structural repose confirms `Y`), and the K-S center `Y` is kept

#### Scenario: A resting tonic with no anchored functional dominant is never demoted
- **WHEN** the K-S center appears as a stable chord and no functional dominant resolves to an anchored predominant-repose `X`
- **THEN** no path fires and the K-S center is kept
- **AND** the functional baseline invariants and center corroboration are unchanged

#### Scenario: A blues/mixolydian I7 is not demoted
- **WHEN** the tonic is a constant dominant seventh (e.g. a `C7 F7 G7` blues) so the resolution target also appears only as a dominant, with no stable point of repose
- **THEN** all paths abort and the dominant-quality tonic is kept (the blues/mixolydian character is handled as coloring, not as a functional dominant)

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
- **WHEN** the K-S center is not exposed as a dominant resolving to a resting target under any path
- **THEN** the detected key equals the K-S / within-band corroboration result
