# applied-dominant-analysis Specification

## Purpose

The analyzer identifies applied (secondary) dominants and tritone substitutes within a chord sequence, labeling dominant-seventh chords by their resolution relationship to a target chord. This surfaces functional harmony beyond the diatonic, distinguishing genuine dominant resolutions from their inverses.
## Requirements
### Requirement: Secondary dominant detection by descending fifth

The analyzer SHALL identify a dominant-seventh chord as a secondary dominant `V7/x` when it resolves to a target chord a perfect fifth below (equivalently, the target root is a perfect fourth — five semitones — above the dominant root), where the target is a non-tonic scale degree or its tonicization. The relationship MUST be the descending-fifth resolution, not its inverse.

#### Scenario: E7 to Am in C major is V7/vi
- **WHEN** in C major the chord `E7` is followed by `Am`
- **THEN** `E7` is labeled a secondary dominant targeting the sixth degree (`V7/vi`)

#### Scenario: D7 to G in C major is V7/V
- **WHEN** in C major the chord `D7` is followed by `G`
- **THEN** `D7` is labeled a secondary dominant targeting the fifth degree (`V7/V`)

#### Scenario: The inverted relationship is not a secondary dominant
- **WHEN** a dominant-seventh chord is followed by a chord a perfect fifth above its root (the reverse of a dominant resolution)
- **THEN** it is NOT labeled a secondary dominant on that basis

### Requirement: Tritone substitute (SubV) detection

The analyzer SHALL identify a dominant-seventh chord as a tritone substitute (`SubV`, i.e. `bII7`) when its root lies a semitone above the resolution target and it resolves down by a semitone. The detection MUST place the substitute a semitone above the target, not below.

#### Scenario: Db7 to C is SubV of the tonic
- **WHEN** the chord `Db7` resolves to `C` (the tonic)
- **THEN** `Db7` is labeled a tritone substitute (`SubV`)

#### Scenario: SubV shares the tritone of the dominant it replaces
- **WHEN** `Db7` is identified as `SubV` resolving to `C`
- **THEN** its guiding tritone matches that of `G7` (the `V7` it substitutes)

#### Scenario: A dominant a semitone below the target is not SubV
- **WHEN** a dominant-seventh chord sits a semitone below its following chord
- **THEN** it is NOT labeled a tritone substitute on that basis

### Requirement: Dominant-quality chords without dominant function

The analyzer SHALL recognize that a dominant-seventh-quality chord which does NOT resolve as `V7→I` or `SubV7→I` may carry a non-dominant function determined by context, and SHALL classify it accordingly rather than defaulting to a secondary dominant. Per Chediak (pp. 111–113): `bVII7` is a minor subdominant (modal interchange in a major key); `I7` and `IV7` are blues chords; a `VII7` resolving directly to `I` is cadential (otherwise `V7/III`); `II7` and `bVI7` are altered subdominants related by tritone.

#### Scenario: bVII7 is a minor subdominant, not a secondary dominant
- **WHEN** in C major the chord `Bb7` resolves up a whole step to `C`
- **THEN** it is classified as a minor-subdominant / modal-interchange chord (`bVII7`)
- **AND** it is NOT labeled a secondary dominant

#### Scenario: Blues sevenths on I and IV are not secondary dominants
- **WHEN** in C major `C7` (`I7`) and `F7` (`IV7`) appear in a blues context
- **THEN** each is classified as a blues chord, not a secondary dominant

#### Scenario: VII7 resolving to the tonic is cadential
- **WHEN** in C major a long `B7` resolves directly to `C` and is not preceded by a ii cadential
- **THEN** it is classified as a cadential `VII7`
- **AND** a short `B7` in the `F#m7 B7` cliché is classified as `V7/III` instead

#### Scenario: A genuine secondary dominant is still detected
- **WHEN** in C major `E7` resolves to `Am`
- **THEN** it remains a secondary dominant targeting the sixth degree (`V7/vi`)

### Requirement: Diminished seventh as a rootless dominant (V7(b9))

The analyzer SHALL recognize a diminished-seventh chord (`dim7`/`°7`) as a **rootless
dominant with a flat ninth** — a `V7(b9)` whose fundamental is omitted. The implied
dominant root is a major third (four semitones) below the written diminished root, and the
chord's tonic of resolution is a semitone above the written diminished root. Equivalently,
`B°7` (B-D-F-Ab) is `G7(b9)` (G-B-D-F-Ab) without the G, resolving to C.

The analyzer SHALL classify a `dim7` as a dominant ONLY when it resolves to a target chord
whose root (or bass) is a **semitone above** the diminished chord's written root. When it
does, the analyzer SHALL label it as a dominant of that target — a primary dominant when the
target is the tonic (`V7(b9)` of I), or a **secondary rootless dominant** when the target is
another scale degree or its tonicization (`V7(b9)/x`), mirroring the existing `V7/x`
labeling. This holds whether the diminished chord is diatonic (`vii°7`) or chromatic
(`#i°7`, `#ii°7`, `#iv°7`).

#### Scenario: Diatonic vii°7 is the rootless dominant of the tonic
- **WHEN** in C major the chord `B°7` resolves to `C`
- **THEN** it is read as a rootless dominant of the tonic (`V7(b9)` of I, implied G root)
- **AND** the relationship cites that `B°7` = `G7(b9)` without the fundamental

#### Scenario: Ascending #i°7 is a secondary rootless dominant of ii
- **WHEN** in C major the chord `C#°7` resolves to `Dm`
- **THEN** it is labeled a secondary rootless dominant targeting the second degree (`V7(b9)/ii`, implied A root)

#### Scenario: #iv°7 is a secondary rootless dominant of V
- **WHEN** in C major the chord `F#°7` resolves to `G`
- **THEN** it is labeled a secondary rootless dominant targeting the fifth degree (`V7(b9)/V`, implied D root)

#### Scenario: The dominant reading resolves a semitone above the written root
- **WHEN** a `dim7` is classified as a dominant
- **THEN** the target chord's root or bass lies exactly one semitone above the diminished chord's written root
- **AND** the implied dominant root lies a major third below that written root

### Requirement: Diminished seventh of approach carries no dominant function

The analyzer SHALL NOT label a diminished-seventh chord as a dominant when it does not
resolve a semitone above its written root (a chromatic passing or auxiliary diminished — a
neighbor figure, or an approach that does not complete the rootless-dominant resolution).
Such a chord SHALL be reported as a diminished chord of approach/passing, not a secondary
dominant, so that the symmetry of `dim7` does not cause every diminished chord to be read as
a dominant.

#### Scenario: A diminished chord that does not resolve a semitone up is not a dominant
- **WHEN** a `dim7` is followed by a chord whose root is not a semitone above the diminished root (e.g. a return to the same chord, or a descending chromatic approach)
- **THEN** it is NOT labeled a dominant on that basis
- **AND** it is reported as a passing/auxiliary diminished chord

#### Scenario: The visual diminished notation is preserved
- **WHEN** a `dim7` is read as a rootless dominant
- **THEN** its roman-numeral symbol still displays the diminished mark (`vii°7`, `#i°7`)
- **AND** the dominant reading appears as a functional gloss (e.g. "`#i°7` = V7(b9)/ii"), not as a replacement of the numeral

