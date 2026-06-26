## ADDED Requirements

### Requirement: Chord-scale mapping

The analyzer SHALL map each chord, in the context of the active key/mode and its degree/function, to one or more recommended chord-scales (e.g. Ionian on Imaj7, Dorian on iim7, Mixolydian on V7, Locrian on iiø7).

#### Scenario: Tonic major maps to Ionian
- **WHEN** in C major the chord `Cmaj7` (I) is analyzed
- **THEN** a recommended chord-scale of C Ionian is reported

#### Scenario: ii chord maps to Dorian
- **WHEN** in C major the chord `Dm7` (ii) is analyzed
- **THEN** a recommended chord-scale of D Dorian is reported

#### Scenario: Dominant maps to Mixolydian by default
- **WHEN** in C major the chord `G7` (V) is analyzed
- **THEN** a recommended chord-scale of G Mixolydian is reported

#### Scenario: Half-diminished maps to Locrian
- **WHEN** the chord `Dm7b5` functions as iiø7
- **THEN** a recommended chord-scale of Locrian is reported

### Requirement: Available tensions and avoid notes

For a chord and its recommended chord-scale, the analyzer SHALL list the available tensions (9, 11, 13 and alterations present in the scale, a whole step above a chord tone) and flag avoid notes (scale notes a semitone above a chord tone that clash).

#### Scenario: Imaj7 has a natural-11 avoid note
- **WHEN** `Cmaj7` is analyzed with the Ionian chord-scale
- **THEN** tensions `9` and `13` are listed as available
- **AND** the natural `11` (F, a semitone above the major third E) is flagged as an avoid note

#### Scenario: iim7 (Dorian) makes the 11 available
- **WHEN** `Dm7` is analyzed with the Dorian chord-scale
- **THEN** tensions `9`, `11`, and `13` are listed as available

#### Scenario: Tensions are reported per chord
- **WHEN** any chord is analyzed with a recommended chord-scale
- **THEN** the result associates that chord with its available tensions and avoid notes
