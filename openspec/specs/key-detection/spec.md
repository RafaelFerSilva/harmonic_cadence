# key-detection Specification

## Purpose

The analyzer estimates tonality from a chord sequence by building a pitch-class profile and correlating it against the Krumhansl-Schmuckler key profiles, replacing the prior first-chord/minor-ratio heuristic. It also segments modulating pieces into contiguous tonal regions so they are not forced into a single key.
## Requirements
### Requirement: Pitch-class profile from chords

The analyzer SHALL derive a 12-bin pitch-class profile from a chord sequence by accumulating each chord's realized pitch classes, as the input to key detection.

#### Scenario: Profile accumulates chord tones
- **WHEN** a profile is built from the chords `C`, `F`, `G`
- **THEN** every pitch class present in those chords has a non-zero weight
- **AND** pitch classes absent from all three have zero weight

### Requirement: Krumhansl-Schmuckler key detection

The analyzer SHALL estimate tonality by correlating the pitch-class profile against
the 24 major/minor Krumhansl-Schmuckler key profiles, returning the best-scoring key
together with a confidence/ranking. This SHALL replace the first-chord/minor-ratio
heuristic. The replacement SHALL be complete: **every** analysis entry point that
needs a key — including the standalone functional-parse and reharmonization helpers
that accept a chord sequence without a provider — SHALL use this K-S detection. No
first-chord/minor-ratio fallback heuristic may remain in the codebase.

#### Scenario: Diatonic C-major progression detects C major
- **WHEN** key detection runs on a clearly C-major progression (e.g. `C F G C Am Dm G C`)
- **THEN** the top-ranked key is C major

#### Scenario: Result carries a confidence and runners-up
- **WHEN** key detection returns a result
- **THEN** it includes the chosen key, a numeric score, and at least the next best alternative
- **AND** a near-tie between relative major/minor is reflected in close scores

#### Scenario: Detection does not depend on the first chord
- **WHEN** a progression is rotated to start on a non-tonic chord while still resolving to the same tonic at the end
- **THEN** the detected key is unchanged
- **AND** the estimate is driven by the overall content and the cadential resolution, not by which chord happens to be first

#### Scenario: Standalone parse and reharmonization use K-S detection
- **WHEN** the standalone functional-parse or reharmonization helper is called with a
  chord sequence and no explicit key
- **THEN** the key it analyzes against is the one returned by K-S detection
- **AND** no first-chord/minor-ratio heuristic is consulted

### Requirement: Modulation segmentation

The analyzer SHALL segment a chord sequence into contiguous tonal regions when the local key estimate changes, so a modulating piece is not forced into a single key.

#### Scenario: A key change yields multiple regions
- **WHEN** a sequence clearly establishes one key and then another (e.g. a section in C major followed by a section in Eb major)
- **THEN** the analysis reports more than one tonal region
- **AND** each region carries its own detected key and span

#### Scenario: A single-key piece yields one region
- **WHEN** the sequence stays in one key throughout
- **THEN** exactly one tonal region spanning the whole sequence is reported

### Requirement: Mode-aware tonal estimate

The key estimate SHALL be able to report a church mode (beyond `major`/`minor`) when the diatonic collection and tonal center indicate one, in coordination with `modal-tonal-center`. The existing major/minor detection and its result shape MUST remain valid.

#### Scenario: Modal piece reports its mode
- **WHEN** key detection runs on a clearly mixolydian progression centered on G
- **THEN** the estimate exposes a mode of `mixolydian` for that center

#### Scenario: Tonal piece still reports major or minor
- **WHEN** key detection runs on a standard tonal progression with a leading tone
- **THEN** the estimate's mode is `major` or `minor` as before
- **AND** existing callers reading the major/minor result continue to work

### Requirement: Cadential corroboration disambiguates near-tie keys

The analyzer SHALL break a near-tie between the top Krumhansl-Schmuckler key candidates using a cadential corroboration of the tonal center — functional signals the pitch-class histogram discards: the first chord, the final chord, and an authentic cadence near the end. The tonal anchor is the **bass** (not the chord root): "settles on the tonic" and the cadence target use the lowest sounding note, so a chord over a tonic pedal (e.g. `D/A` in A) anchors the bass, not the printed root. The authentic cadence is a **dominant-function chord resolving to the tonic** — the dominant (a fifth above) or its tritone substitute (`bII7`), both idiomatic in MPB/bossa. A near-tie is when candidate scores fall within a band of the top K-S score (`TIE_BAND=0.10`); this targets the systematic major ↔ relative-minor confusion, where the two keys share a diatonic collection and are therefore a structural near-tie.

The corroboration SHALL act **only within the near-tie band**, EXCEPT for the functional-dominant quality gate defined in its own requirement: a candidate whose K-S score is clearly above the others MUST NOT be overridden by within-band corroboration, but the center MAY be corrected **beyond** the band by the quality gate when the K-S center is exposed as a mere dominant. The returned estimate keeps the same shape (chosen key, score, and alternatives), and downstream behavior (mode-vs-key arbitration, modulation segmentation) is unchanged.

#### Scenario: A relative near-tie is decided by the final authentic cadence

- **WHEN** a progression's top K-S candidates are a relative major/minor pair within
  the tie band, and the progression ends with an authentic cadence to the major tonic
  (the dominant of that tonic resolving to it, e.g. `G7 → C`)
- **THEN** the detected key is the major key corroborated by that cadence
- **AND** a progression ending `E7 → Am` instead resolves to the relative minor

#### Scenario: A confident K-S result is not overridden by within-band corroboration

- **WHEN** one key scores clearly above all others (outside the near-tie band, i.e. gap > 0.10)
- **THEN** within-band cadential corroboration does not change the detected key
- **AND** the result equals the plain K-S estimate UNLESS the functional-dominant quality gate corrects the center (see that requirement)

#### Scenario: A near-tie with gap up to 0.10 enters the corroboration band

- **WHEN** the gap between the top K-S candidate and the correct key is between 0.06 and 0.10
- **THEN** the correct key enters the band and corroboration can select it
- **AND** the corroboration signal (authentic cadence, final chord quality) determines the winner

#### Scenario: Diatonic textbook progressions are unaffected

- **WHEN** key detection runs on a clearly diatonic major progression (e.g.
  `C F G C Am Dm G C`)
- **THEN** the detected key is unchanged from K-S (C major)
- **AND** the synthetic regression corpus stays at its established accuracy

#### Scenario: Result shape and contract are preserved

- **WHEN** `detect_key` returns an estimate after corroboration
- **THEN** it is the same `KeyEstimate` shape (chosen key, numeric score, alternatives)
- **AND** existing callers reading the key/mode/alternatives continue to work

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

### Requirement: Anchor gate recovers an I7-funk center detected as its IV

The analyzer SHALL correct the Krumhansl-Schmuckler center estimate `Y` to a candidate `X`
when a song has an **I7-funk** center (Chediak XXXIV: the seventh over the tonic is a special
blues/funk function, not a dominant) that K-S mistakes for its subdominant. This is the
**inverse geometry** of the functional-dominant quality gate: there the engine picks the V and
corrects down a fifth; here the funk tonic `X` is voiced as a dominant-seventh (`I7`), its IV
(`Y = (X + 5) mod 12`) is more frequent and rests, so K-S picks the IV, and the correction is
to a center a fifth **above** the guess. Because the funk tonic offers no V→I cadence and loses
on frequency, the recovering signal is **structural** (the piece opens and closes on `X`), not
statistical or cadential.

The correction SHALL be ultraconservative — firing only when ALL of the following hold, each
encoding a property of the I7-funk pattern:

1. the first and last chords share root `X` (the piece opens and closes "at home");
2. the K-S winner `Y` is the IV of `X` (`Y == (X + 5) mod 12`, `X != Y`);
3. `X` appears as a dominant-seventh somewhere (the tonic sounds like a dominant — `I7` funk);
4. `X` also appears as a plain major triad somewhere (it genuinely rests — distinguishing a
   funk tonic from a mere V pedal, where `X` would appear only as `X7`);
5. `X` is among the top-2 K-S alternatives (not a wild flip).

This path SHALL be geometrically separate from the V-as-tonic gate (which corrects down a
fifth, anchored on functional resolution) and SHALL NOT alter the K-S correlation or the
cadential-corroboration stage.

#### Scenario: An I7-funk tonic detected as its IV is recovered
- **WHEN** a song opens and closes on `E`, `E` appears both as `E7` and as a plain `E` triad, and K-S picks `A` (the IV of `E`, with `E` as a top-2 alternative)
- **THEN** the detected center is corrected to `E`

#### Scenario: A confident non-funk key is untouched
- **WHEN** the piece does not open and close on the same root, or the K-S winner is not the IV of that root
- **THEN** the anchor gate does not fire and the K-S center stands

#### Scenario: A pure V pedal is not mistaken for an I7-funk tonic
- **WHEN** a song opens and closes on `X` but `X` appears only as a dominant-seventh (never as a resting major triad)
- **THEN** the anchor gate does not fire (guard 4 fails) and the K-S center stands

### Requirement: Parallel mode correction at the anchored tonic

The analyzer SHALL correct a parallel mode confusion (same tonic, major ↔ minor) by inverting the detected mode when, at the tonic the piece is anchored on, the quality of the tonic chords contradicts the Krumhansl-Schmuckler mode. The cadence cannot distinguish parallel keys (the dominant is shared — `G7` is the V of both C major and C minor), so the discriminator is the quality of the tonic-rooted chords (the third of the tonic defines the mode). The correction acts only when the detected tonic is the tonal anchor — the final bass is that tonic, or an authentic cadence (the dominant or its tritone substitute) resolves to it — and the net tonic-chord quality vote (minor minus major) is decisive. This bass-anchor gate keeps the correction from touching a relative-confusion case, where the detected tonic is an impostor.

The correction adjusts only the mode (the tonic from K-S is kept), composes with the cadential tie-break (which decides the tonic), and preserves the `KeyEstimate` shape; downstream mode-vs-key arbitration and segmentation are unchanged.

#### Scenario: A minor piece read as parallel major is corrected

- **WHEN** the K-S estimate is a major key but the piece is anchored on that tonic (settles on it or cadences to it) and the tonic chords are predominantly minor (e.g. an end like `G7 → Cm` over recurring `Cm`)
- **THEN** the detected mode is corrected to minor (the parallel)
- **AND** the detected tonic is unchanged

#### Scenario: A relative-confusion impostor tonic is not touched

- **WHEN** the detected tonic is NOT the anchor (the piece cadences elsewhere, e.g. detected A minor but the cadence resolves to C)
- **THEN** the parallel mode correction does not fire
- **AND** the mode is left as the K-S/tie-break result

#### Scenario: A major piece with isolated minor borrowings is not flipped

- **WHEN** a major key is anchored on its tonic but only an isolated minor tonic chord appears (the net tonic-quality vote is below the threshold)
- **THEN** the mode stays major

#### Scenario: Result shape and contract preserved

- **WHEN** `detect_key` returns an estimate after a mode correction
- **THEN** it is the same `KeyEstimate` shape, with the score reflecting the corrected key
- **AND** existing callers reading key/mode/alternatives continue to work

### Requirement: Dominant-region post-processing of segmentation output

The analyzer SHALL provide a `dominant_regions` function that post-processes the raw output of `segment_keys` into a reduced set of structurally meaningful regions by merging adjacent same-key fragments and eliminating regions whose chord count falls below a configurable percentage threshold of the total. The underlying `segment_keys` function and its window size SHALL remain unchanged.

#### Scenario: Small regions are absorbed into neighbours
- **WHEN** `dominant_regions` receives regions where one region spans fewer than `min_pct` of the total chords
- **THEN** that region is merged into the adjacent region of the same tonality (if one exists) or the adjacent region with the closest K-S score
- **AND** no region in the output spans fewer than `min_pct` of the total chords

#### Scenario: Adjacent same-key fragments are consolidated
- **WHEN** two adjacent regions carry the same key (same tonic and mode), as can happen when a segment boundary falls inside a tonal plateau
- **THEN** they are merged into a single region spanning both

#### Scenario: A piece with two clear tonal areas yields two regions
- **WHEN** `dominant_regions` processes a bimodal piece like Chega de Saudade (D minor intro + D major refrão)
- **THEN** the output contains exactly two dominant regions: one for D minor and one for D major
- **AND** each region spans at least `min_pct` of the total chords

#### Scenario: A single-key piece yields one region
- **WHEN** a chord sequence stays in one key throughout
- **THEN** `dominant_regions` returns a single region, same as `segment_keys`

#### Scenario: segment_keys is not modified
- **WHEN** `segment_keys` is called directly
- **THEN** its output is identical to before this change (window=8, no post-processing)

