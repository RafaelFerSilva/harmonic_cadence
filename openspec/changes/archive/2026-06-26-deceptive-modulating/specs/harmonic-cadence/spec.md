## ADDED Requirements

### Requirement: Deceptive cadences distinguish diatonic from modulating

A deceptive cadence (V → a non-tonic) SHALL be reported as **diatonic** when the resolution stays within the current tonal region, and as **modulating** when the resolution crosses into a different tonal region — a key change detected by the modulation analysis (`segment_keys`). When no tonal-region information is available, a deceptive cadence defaults to diatonic.

#### Scenario: Deceptive within one key is diatonic
- **WHEN** `G7 Am` (V→vi) occurs and both chords belong to the same tonal region (C major)
- **THEN** a diatonic deceptive cadence is reported

#### Scenario: Deceptive across a key change is modulating
- **WHEN** a `V` is followed by a chord that begins a different tonal region (a detected key change)
- **THEN** a modulating deceptive cadence is reported for that pair

#### Scenario: Without region information, deceptive defaults to diatonic
- **WHEN** a deceptive `V`→non-tonic is analyzed with no tonal-region information
- **THEN** it is reported as a diatonic deceptive cadence
