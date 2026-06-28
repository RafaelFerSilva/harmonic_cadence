## MODIFIED Requirements

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

## ADDED Requirements

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
