## MODIFIED Requirements

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
