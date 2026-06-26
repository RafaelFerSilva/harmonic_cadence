## ADDED Requirements

### Requirement: Dominant chords map to a dominant chord-scale

A dominant-seventh-quality chord SHALL map to a dominant chord-scale determined by its position relative to the key, NOT to the diatonic-degree scale of its root. Per Chediak (Vol. I, p. 113): the primary `V7` and the blues `I7` map to Mixolydian; the special-function dominants `IV7`, `bVII7`, `II7`, `bVI7`, and `VII7` map to the Lydian-dominant scale (lídio b7, also Chediak's "nordestino" mode, p. 121); other dominants default to Mixolydian.

#### Scenario: A blues I7 maps to Mixolydian, not Ionian
- **WHEN** in C major the dominant chord `C7` (I7) is analyzed
- **THEN** its recommended chord-scale is C Mixolydian
- **AND** it is NOT C Ionian

#### Scenario: A bVII7 maps to Lydian dominant
- **WHEN** in C major the chord `Bb7` (bVII7) is analyzed
- **THEN** its recommended chord-scale is Bb Lydian-dominant (lídio b7)

#### Scenario: A IV7 maps to Lydian dominant
- **WHEN** in C major the chord `F7` (IV7) is analyzed
- **THEN** its recommended chord-scale is F Lydian-dominant

#### Scenario: Non-dominant diatonic chords are unchanged
- **WHEN** `Cmaj7`, `Dm7`, and `G7` are analyzed in C major
- **THEN** they map to Ionian, Dorian, and Mixolydian respectively
