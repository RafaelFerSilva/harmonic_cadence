## ADDED Requirements

### Requirement: Auxiliary dominant (dominant of a modal-interchange chord)

The analyzer SHALL identify a dominant-seventh chord as an **auxiliary dominant** when it resolves a perfect fifth below (the target root a perfect fourth — five semitones — above the dominant root) to a target that is a **modal-interchange (borrowed) chord** — i.e. a chromatic, non-diatonic, non-tonic target. This mirrors the secondary dominant (same descending-fifth motion) but is distinguished by the **nature of the target**: the secondary dominant prepares a diatonic degree, the auxiliary dominant prepares a borrowed chord (`V7/bIII`, `V7/bVI`, `V7/bVII`…). Per Chediak (Vol. I, XVIII-b, p.99). The auxiliary dominant carries dominant function.

This resolution-based reading SHALL take precedence over labeling the chord a special-function `bVII7`/`bVI7` (minor subdominant): a `bVII7` or `bVI7` that **resolves a fifth below** is an auxiliary dominant, whereas one that does **not** so resolve keeps its minor-subdominant reading. The `I7` and `IV7` blues chords (Chediak XXXIV) are NOT reinterpreted as auxiliary dominants.

#### Scenario: bVII7 resolving a fifth below is an auxiliary dominant
- **WHEN** in C major `Bb7` resolves a perfect fifth below to `Eb` (a bIII modal-interchange chord)
- **THEN** it is labeled an auxiliary dominant targeting that borrowed chord (`V7/bIII`)
- **AND** it is NOT labeled a minor-subdominant `bVII7` (`Emp`)

#### Scenario: A dominant resolving to a borrowed bVI is an auxiliary dominant
- **WHEN** in C major `Eb7` resolves a perfect fifth below to `Ab` (a bVI borrowed chord)
- **THEN** it is labeled an auxiliary dominant (`V7/bVI`)
- **AND** it is NOT labeled `V7/None` or a modal borrowing

#### Scenario: bVII7 that does not resolve a fifth below stays a minor subdominant
- **WHEN** in C major `Bb7` resolves up a whole step to `C` (the tonic), not a fifth below
- **THEN** it keeps its minor-subdominant `bVII7` reading and is NOT an auxiliary dominant

#### Scenario: The blues I7/IV7 are not auxiliary dominants
- **WHEN** in C major `C7` (`I7`) moves to `F`, or `F7` (`IV7`) moves to `Bb`
- **THEN** each keeps its blues reading and is NOT relabeled an auxiliary dominant

### Requirement: Secondary tritone substitute (SubV7) of a diatonic degree

The analyzer SHALL identify a dominant-seventh chord as a **secondary tritone substitute** (`SubV7/x`) when its root lies a **semitone above** a target chord that is a **diatonic degree other than the tonic**, resolving down by a semitone to it. Per Chediak (Vol. I, XVIII-c, p.99): the `SubV7` of the diatonic degrees, whose resolution is the bass descending a semitone to reach the desired chord. This extends the existing tonic-only `SubV` (`bII7→I`) to the secondary degrees (`SubV7/ii`, `SubV7/V`…).

This resolution-based reading SHALL take precedence over labeling the chord a special-function `bVI7`: an `Ab7` that resolves a semitone down to a diatonic `G` (the V) is `SubV7/V`, not a `bVI7` modal borrowing.

#### Scenario: Ab7 resolving down a semitone to V is SubV7/V
- **WHEN** in C major `Ab7` resolves down a semitone to `G` (the diatonic dominant)
- **THEN** it is labeled a secondary tritone substitute targeting the fifth degree (`SubV7/V`)
- **AND** it is NOT labeled a `bVI7` modal borrowing (`Emp`)

#### Scenario: Eb7 resolving down a semitone to ii is SubV7/ii
- **WHEN** in C major `Eb7` resolves down a semitone to `Dm` (the diatonic supertonic)
- **THEN** it is labeled a secondary tritone substitute targeting the second degree (`SubV7/ii`)

#### Scenario: The primary SubV (to the tonic) is unchanged
- **WHEN** `Db7` resolves down a semitone to `C` (the tonic)
- **THEN** it keeps its primary `SubV` reading (`bII7 → I`), not a secondary label

#### Scenario: A genuine secondary dominant is still detected
- **WHEN** in C major `D7` resolves a fifth below to `G`
- **THEN** it remains a secondary dominant (`V7/V`), not an auxiliary dominant (the target `G` is diatonic)
