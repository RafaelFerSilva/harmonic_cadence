# harmonic-cadence Specification

## Purpose
TBD - created by archiving change cadence-taxonomy. Update Purpose after archive.
## Requirements
### Requirement: The five harmonic cadences

The analyzer SHALL classify harmonic cadences into Chediak's five types (Vol. I, pp. 109-111): **perfect** (V→I in root position), **imperfect** (V→I with an inversion, or VII→I), **plagal** (IV→I or iim→I), **half** (any degree → V), and **deceptive** (V → any degree that is not the tonic). It SHALL additionally recognize the **authentic** cadence — a perfect cadence preceded by a subdominant (IV or ii → V → I). Classification is by scale-degree position, so it applies in both major and minor.

#### Scenario: Perfect cadence is root-position V–I
- **WHEN** the progression `G7 C` (V→I) occurs with both chords in root position in C major
- **THEN** a perfect cadence is reported for `G7 → C`

#### Scenario: An inverted V–I is imperfect, not perfect
- **WHEN** `G7 C/E` (V→I with the tonic inverted) occurs in C major
- **THEN** an imperfect cadence is reported
- **AND** it is NOT reported as a perfect cadence

#### Scenario: VII–I is an imperfect cadence
- **WHEN** `Bm7b5 C` (vii→I) occurs in C major
- **THEN** an imperfect cadence is reported

#### Scenario: Plagal includes the ii–I shape
- **WHEN** `F C` (IV→I) or `Dm C` (ii→I) occurs in C major
- **THEN** a plagal cadence is reported for each

#### Scenario: Deceptive is V to any non-tonic
- **WHEN** `G7 Am` (V→vi) or `G7 F` (V→IV) occurs in C major
- **THEN** a deceptive cadence is reported for each

#### Scenario: Half cadence rests on the dominant
- **WHEN** `Dm G` (ii→V) occurs in C major
- **THEN** a half cadence is reported

#### Scenario: Authentic cadence is a prepared perfect cadence
- **WHEN** `Dm7 G7 C` (ii→V→I) occurs in C major
- **THEN** an authentic cadence is reported for the three-chord progression

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

