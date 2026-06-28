## MODIFIED Requirements

### Requirement: Cadential corroboration disambiguates near-tie keys

The analyzer SHALL break a near-tie between the top Krumhansl-Schmuckler key candidates using a cadential corroboration of the tonal center — functional signals the pitch-class histogram discards: the first chord, the final chord, and an authentic cadence near the end. The tonal anchor is the **bass** (not the chord root): "settles on the tonic" and the cadence target use the lowest sounding note, so a chord over a tonic pedal (e.g. `D/A` in A) anchors the bass, not the printed root. The authentic cadence is a **dominant-function chord resolving to the tonic** — the dominant (a fifth above) or its tritone substitute (`bII7`), both idiomatic in MPB/bossa. A near-tie is when candidate scores fall within a band of the top K-S score (`TIE_BAND=0.10`); this targets the systematic major ↔ relative-minor confusion, where the two keys share a diatonic collection and are therefore a structural near-tie.

The corroboration SHALL act **only within the near-tie band**: a candidate whose K-S score is clearly above the others MUST NOT be overridden. The returned estimate keeps the same shape (chosen key, score, and alternatives), and downstream behavior (mode-vs-key arbitration, modulation segmentation) is unchanged.

#### Scenario: A relative near-tie is decided by the final authentic cadence

- **WHEN** a progression's top K-S candidates are a relative major/minor pair within the tie band, and the progression ends with an authentic cadence to the major tonic (the dominant of that tonic resolving to it, e.g. `G7 → C`)
- **THEN** the detected key is the major key corroborated by that cadence
- **AND** a progression ending `E7 → Am` instead resolves to the relative minor

#### Scenario: A confident K-S result is not overridden

- **WHEN** one key scores clearly above all others (outside the near-tie band, i.e. gap > 0.10)
- **THEN** cadential corroboration does not change the detected key
- **AND** the result equals the plain K-S estimate

#### Scenario: A near-tie with gap up to 0.10 enters the corroboration band

- **WHEN** the gap between the top K-S candidate and the correct key is between 0.06 and 0.10
- **THEN** the correct key enters the band and corroboration can select it
- **AND** the corroboration signal (authentic cadence, final chord quality) determines the winner

#### Scenario: Diatonic textbook progressions are unaffected

- **WHEN** key detection runs on a clearly diatonic major progression (e.g. `C F G C Am Dm G C`)
- **THEN** the detected key is unchanged from K-S (C major)
- **AND** the synthetic regression corpus stays at its established accuracy

#### Scenario: Result shape and contract are preserved

- **WHEN** `detect_key` returns an estimate after corroboration
- **THEN** it is the same `KeyEstimate` shape (chosen key, numeric score, alternatives)
- **AND** existing callers reading the key/mode/alternatives continue to work
