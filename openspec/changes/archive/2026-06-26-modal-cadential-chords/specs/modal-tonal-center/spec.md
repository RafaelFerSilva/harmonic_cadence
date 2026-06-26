## ADDED Requirements

### Requirement: Characteristic cadential and avoided chords per mode

When a mode is active, the analyzer SHALL expose the mode's characteristic cadential chords and its avoided chords, per Chediak (Vol. I, pp. 122-125), alongside the mode's characteristic note. These are the source's curated selection (which chords firm up the modal flavor in a cadence, and which pull back to major/minor tonality), not a derivation of the diatonic field.

#### Scenario: Dorian cadential and avoided chords
- **WHEN** the active mode is dorian
- **THEN** the cadential chords are `IIm7`, `IV7`, `bVII7M`
- **AND** the avoided chord is `VIm7(b5)`

#### Scenario: Mixolydian cadential and avoided chords
- **WHEN** the active mode is mixolydian
- **THEN** the cadential chords are `I7`, `Vm7`, `bVII7M`
- **AND** the avoided chord is `IIIm7(b5)`

#### Scenario: Phrygian cadential and avoided chords
- **WHEN** the active mode is phrygian
- **THEN** the cadential chords are `bII7M`, `bVIIm7`
- **AND** the avoided chords include `Vm7(b5)` and `bIII7`

#### Scenario: The active modal section exposes the selection
- **WHEN** a piece with an active mode is analyzed
- **THEN** its modal analysis section reports the characteristic note, the cadential chords, and the avoided chords
