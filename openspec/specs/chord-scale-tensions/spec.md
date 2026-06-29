# chord-scale-tensions Specification

## Purpose

The analyzer maps each chord, in the context of the active key/mode and its degree/function, to one or more recommended chord-scales, and lists the available tensions while flagging avoid notes for each chord-scale pairing.
## Requirements
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

### Requirement: Altered dominants map to their altered chord-scale

An altered dominant-seventh chord SHALL map to its altered chord-scale per Chediak (Vol. I, pp. 349-352), and this mapping SHALL take precedence over the position-based dominant mapping. A flat fifth or sharp eleventh maps to the lydian-dominant scale; a sharp fifth maps to the whole-tone scale; a flat ninth maps to the diminished (half-whole) scale; a sharp ninth (or a combined flat-and-sharp ninth) maps to the altered scale. A dominant with no such alteration keeps its position-based scale.

#### Scenario: Flat-ninth dominant maps to the diminished scale
- **WHEN** in C major the chord `G7(b9)` is analyzed
- **THEN** its recommended chord-scale is the G diminished (half-whole) scale

#### Scenario: Sharp-ninth dominant maps to the altered scale
- **WHEN** `G7(#9)` is analyzed
- **THEN** its recommended chord-scale is the G altered scale

#### Scenario: Sharp-fifth dominant maps to the whole-tone scale
- **WHEN** `G7(#5)` is analyzed
- **THEN** its recommended chord-scale is the G whole-tone scale

#### Scenario: Flat-fifth or sharp-eleventh dominant maps to lydian dominant
- **WHEN** `G7(b5)` or `G7(#11)` is analyzed
- **THEN** its recommended chord-scale is the G lydian-dominant scale

#### Scenario: ± dialect alterations are honored
- **WHEN** `G7(9-)` (Cifra Club notation) is analyzed
- **THEN** its recommended chord-scale equals that of `G7(b9)`

#### Scenario: An unaltered dominant keeps its position-based scale
- **WHEN** a plain `G7` (V) is analyzed in C major
- **THEN** its recommended chord-scale remains G Mixolydian

### Requirement: Diminished-seventh dominants map to the diminished chord-scale

A diminished-seventh chord that functions as a rootless dominant SHALL map to the
**diminished (octatonic) chord-scale** (per applied-dominant-analysis),
consistent with the existing flat-ninth-to-diminished mapping for spelled altered dominants (e.g.
`G7(b9)` already maps to the G diminished half-whole scale). The scale SHALL be the
octatonic collection that contains the chord's notes — equivalently, the diminished
(half-whole) scale of the implied dominant root (a major third below the written diminished
root). A diminished chord of approach/passing (no dominant function) keeps its current
treatment and is NOT given a dominant chord-scale on this basis.

#### Scenario: A vii°7 dominant maps to the diminished scale
- **WHEN** in C major `B°7` resolves to `C` (acting as the rootless dominant of I)
- **THEN** its recommended chord-scale is the diminished (octatonic) scale containing B-D-F-Ab
- **AND** this equals the diminished half-whole scale of the implied G dominant

#### Scenario: A secondary diminished dominant maps to the diminished scale
- **WHEN** in C major `C#°7` resolves to `Dm` (acting as `V7(b9)/ii`)
- **THEN** its recommended chord-scale is the diminished (octatonic) scale containing its notes

#### Scenario: A passing diminished is not given a dominant chord-scale
- **WHEN** a diminished-seventh chord does not function as a rootless dominant
- **THEN** it is NOT mapped to a dominant chord-scale by this requirement

### Requirement: Extended dominants map to the Mixolydian chord-scale

The analyzer SHALL map an **extended dominant** OR an **extended SubV** to the **Mixolydian**
chord-scale regardless of its position relative to the key. An extended dominant is a
dominant-seventh whose next chord is itself a dominant-seventh a perfect fourth above (the
cycle-of-fifths chain of Chediak Vol. I, XXVIII(a), pp.107-108); an extended SubV is a
dominant-seventh that is a member of a descending-semitone chain of dominants of length ≥ 3,
resolving a semitone into another dominant (Chediak XXVIII c/d). Chediak states it explicitly
(p.107, pointing to p.339): the extended dominants take the Mixolydian mode as chord-scale.
This rule SHALL take precedence over the **position-based** dominant mapping (so an extended
`II7`/`IV7`/`bVII7`, which the positional rule would send to the Lydian-dominant scale, maps to
Mixolydian), but SHALL NOT override the **altered**-dominant mapping (an extended dominant
carrying a real alteration keeps its altered chord-scale, since the chord tones demand it).

#### Scenario: An extended II7 maps to Mixolydian, not Lydian-dominant
- **WHEN** in C major `D7` (a `II7`) is followed by `G7` (a dominant a perfect fourth above)
- **THEN** its recommended chord-scale is D Mixolydian
- **AND** NOT D Lydian-dominant (the position-based default for `II7`)

#### Scenario: A non-extended II7 keeps its position-based scale
- **WHEN** in C major `D7` is NOT followed by a dominant a perfect fourth above
- **THEN** its recommended chord-scale stays the position-based default (D Lydian-dominant)

#### Scenario: An extended SubV maps to Mixolydian
- **WHEN** in C major `Eb7` (a `bIII7`) is a member of a descending-semitone chain resolving into `D7`
- **THEN** its recommended chord-scale is Eb Mixolydian
- **AND** NOT the position-based default for its position

