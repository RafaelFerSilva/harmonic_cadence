## ADDED Requirements

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
