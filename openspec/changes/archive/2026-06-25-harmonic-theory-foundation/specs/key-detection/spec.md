## ADDED Requirements

### Requirement: Pitch-class profile from chords

The analyzer SHALL derive a 12-bin pitch-class profile from a chord sequence by accumulating each chord's realized pitch classes, as the input to key detection.

#### Scenario: Profile accumulates chord tones
- **WHEN** a profile is built from the chords `C`, `F`, `G`
- **THEN** every pitch class present in those chords has a non-zero weight
- **AND** pitch classes absent from all three have zero weight

### Requirement: Krumhansl-Schmuckler key detection

The analyzer SHALL estimate tonality by correlating the pitch-class profile against the 24 major/minor Krumhansl-Schmuckler key profiles, returning the best-scoring key together with a confidence/ranking. This SHALL replace the first-chord/minor-ratio heuristic.

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

### Requirement: Modulation segmentation

The analyzer SHALL segment a chord sequence into contiguous tonal regions when the local key estimate changes, so a modulating piece is not forced into a single key.

#### Scenario: A key change yields multiple regions
- **WHEN** a sequence clearly establishes one key and then another (e.g. a section in C major followed by a section in Eb major)
- **THEN** the analysis reports more than one tonal region
- **AND** each region carries its own detected key and span

#### Scenario: A single-key piece yields one region
- **WHEN** the sequence stays in one key throughout
- **THEN** exactly one tonal region spanning the whole sequence is reported
