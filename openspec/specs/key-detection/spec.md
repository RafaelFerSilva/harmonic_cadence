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

When the Krumhansl-Schmuckler estimate centers on a chord that is actually the **dominant**, the analyzer SHALL be able to correct the center beyond the near-tie band — but ONLY via a conservative quality discriminator grounded in functional harmony (Chediak): the **tonic is a point of repose** (it appears as a stable chord — major/minor triad or `maj7`/`6`/`m7`), whereas the **dominant is tension** (it appears as a dominant seventh, carrying the tritone). A center can only be corrected when the evidence is unambiguous, so the established correct detections do not regress.

The gate SHALL override the K-S center `Y` with `X` only when ALL of the following hold:

1. **Y appears exclusively as a dominant seventh.** Every chord rooted on `Y` in the piece is typed `Category.DOMINANT`; if `Y` ever appears as a stable (non-dominant) chord, it rests and IS a legitimate tonic, so the gate does not fire.
2. **Y resolves down a fifth.** Some `Y7` chord resolves so the bass of the following chord lands on `X = (Y − 7) mod 12` (a perfect fifth below).
3. **X is a point of repose.** `X` appears in the piece as a stable chord (`Category.MAJOR` or `Category.MINOR`), confirming it is the tonic the dominant resolves to.

The gate considers only `Category.DOMINANT` chords; a fully-diminished seventh is ineligible (it carries two tritones and no single resolution). If `Y` rests anywhere, or no `Y7` resolves down a fifth, or `X` itself never appears as a stable chord, the gate aborts and the K-S / within-band result stands.

#### Scenario: A dominant detected as tonic is corrected to its resolution target
- **WHEN** the K-S center `Y` appears only as a dominant seventh (e.g. always `C7`, never `C`/`Cmaj7`), that `C7` resolves down a fifth to `F`, and `F` appears as a stable chord (e.g. `Fmaj7`)
- **THEN** the detected center is corrected to `F`
- **AND** this holds even though `F` was outside the near-tie band

#### Scenario: A resting tonic is never demoted
- **WHEN** the K-S center appears at least once as a stable chord (a triad or `maj7`/`m7`/`6`)
- **THEN** the gate does not fire and the K-S center is kept
- **AND** the four Cifra-Club baseline metrics are unchanged

#### Scenario: A blues/mixolydian I7 is not demoted
- **WHEN** the tonic is a constant dominant seventh (e.g. a `C7 F7 G7` blues) so the resolution target also appears only as a dominant, with no stable point of repose
- **THEN** the gate aborts and the dominant-quality tonic is kept (the blues/mixolydian character is handled as coloring, not as a functional dominant)

#### Scenario: A diminished seventh never triggers the gate
- **WHEN** the only tritone-bearing chord on the candidate is a fully-diminished seventh
- **THEN** the gate does not fire (the dim7 is ineligible)

#### Scenario: No qualifying dominant leaves K-S unchanged
- **WHEN** the K-S center is not exposed as an exclusive dominant resolving to a resting target
- **THEN** the detected key equals the K-S / within-band corroboration result

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

