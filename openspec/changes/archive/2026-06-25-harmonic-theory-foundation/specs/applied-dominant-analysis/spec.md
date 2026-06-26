## ADDED Requirements

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
