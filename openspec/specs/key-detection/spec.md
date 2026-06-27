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

The analyzer SHALL break a near-tie between the top Krumhansl-Schmuckler key candidates using a cadential corroboration of the tonal center — functional signals the pitch-class histogram discards: the first chord, the final chord, and an authentic cadence near the end. The tonal anchor is the **bass** (not the chord root): "settles on the tonic" and the cadence target use the lowest sounding note, so a chord over a tonic pedal (e.g. `D/A` in A) anchors the bass, not the printed root. The authentic cadence is a **dominant-function chord resolving to the tonic** — the dominant (a fifth above) or its tritone substitute (`bII7`), both idiomatic in MPB/bossa. A near-tie is when candidate scores fall within a small band of the top K-S score; this targets the systematic major ↔ relative-minor confusion, where the two keys share a diatonic collection and are therefore a structural near-tie.

The corroboration SHALL act **only within the near-tie band**: a candidate whose K-S
score is clearly above the others MUST NOT be overridden. The returned estimate keeps
the same shape (chosen key, score, and alternatives), and downstream behavior
(mode-vs-key arbitration, modulation segmentation) is unchanged.

#### Scenario: A relative near-tie is decided by the final authentic cadence

- **WHEN** a progression's top K-S candidates are a relative major/minor pair within
  the tie band, and the progression ends with an authentic cadence to the major tonic
  (the dominant of that tonic resolving to it, e.g. `G7 → C`)
- **THEN** the detected key is the major key corroborated by that cadence
- **AND** a progression ending `E7 → Am` instead resolves to the relative minor

#### Scenario: A confident K-S result is not overridden

- **WHEN** one key scores clearly above all others (outside the near-tie band)
- **THEN** cadential corroboration does not change the detected key
- **AND** the result equals the plain K-S estimate

#### Scenario: Diatonic textbook progressions are unaffected

- **WHEN** key detection runs on a clearly diatonic major progression (e.g.
  `C F G C Am Dm G C`)
- **THEN** the detected key is unchanged from K-S (C major)
- **AND** the synthetic regression corpus stays at its established accuracy

#### Scenario: Result shape and contract are preserved

- **WHEN** `detect_key` returns an estimate after corroboration
- **THEN** it is the same `KeyEstimate` shape (chosen key, numeric score, alternatives)
- **AND** existing callers reading the key/mode/alternatives continue to work

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

