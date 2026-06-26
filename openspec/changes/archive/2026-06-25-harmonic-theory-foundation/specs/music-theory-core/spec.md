## ADDED Requirements

### Requirement: Spelling-preserving note model

`cifra_core` SHALL provide a `Note` model that preserves enharmonic spelling (letter + accidental) while exposing the pitch class (0–11). Enharmonically equivalent spellings MUST be distinct values that share a pitch class, and the analysis MUST NOT collapse flats into sharps.

#### Scenario: Enharmonic spellings are distinct but share a pitch class
- **WHEN** `Note` is built from `"Db"` and from `"C#"`
- **THEN** the two notes are not equal
- **AND** both report pitch class `1`

#### Scenario: Letter and accidental are recoverable
- **WHEN** a `Note` is parsed from `"Bb"`
- **THEN** its letter is `B` and its accidental is flat
- **AND** rendering it back yields `"Bb"` (not `"A#"`)

### Requirement: Interval between notes

`cifra_core` SHALL compute the interval between two notes as a semitone distance, available as an ascending value in `0–11`.

#### Scenario: Ascending fourth is five semitones
- **WHEN** the interval from `E` up to `A` is computed
- **THEN** the result is `5`

#### Scenario: Tritone is six semitones in both directions
- **WHEN** the interval between `C` and `F#` is computed
- **THEN** the magnitude is `6`

### Requirement: Chord realization into pitch classes

`cifra_core` SHALL realize a chord symbol into its set of pitch classes (root, third, fifth, and any seventh/tensions), so analysis can reason about chord tones rather than the raw symbol string.

#### Scenario: Major seventh chord realizes to four tones
- **WHEN** `"Cmaj7"` is realized
- **THEN** the pitch-class set equals that of `{C, E, G, B}`

#### Scenario: Half-diminished realizes correctly
- **WHEN** `"Dm7b5"` is realized
- **THEN** the pitch-class set equals that of `{D, F, Ab, C}`

#### Scenario: Brazilian 7M notation is a major seventh
- **WHEN** `"C7M"` is realized
- **THEN** it equals the realization of `"Cmaj7"`

### Requirement: Scales and modes as data

`cifra_core` SHALL build the pitch classes of a scale/mode from a tonic, with correct diatonic spelling, for at least the church modes plus harmonic and melodic minor.

#### Scenario: Mixolydian has a flat seventh
- **WHEN** the G Mixolydian scale is built
- **THEN** it contains `F` natural (not `F#`)

#### Scenario: Major scale is spelled with one letter per degree
- **WHEN** the F major scale is built
- **THEN** the fourth degree is spelled `Bb` (not `A#`)
- **AND** each of the seven letters A–G appears exactly once
