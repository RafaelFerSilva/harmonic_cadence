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

**Functional resolution SHALL precede the modal-interchange reading**: a `bVII7`/`bVI7` that
resolves a perfect fourth up into a diatonic target (e.g. `bVII7→bIII` in a minor key) is a
secondary dominant (`Dsec`, `V7/x`) — the `Emp` reading applies only without functional
resolution (Chediak p.114 uses `Bb7→Eb` as a secondary-dominant example).

A `II7` that matches no dominant branch SHALL be classified as an **altered subdominant**
(`SD`, "Subdominante alterada (II7)") per the special-function table (Chediak p.113, quadro:
`II7` → "Subd. alt."). A `VII7` that resolves directly to the tonic remains cadential (`D`);
a `VII7` that does NOT resolve to the tonic SHALL be read as `V7/III` (`Dsec`, expected
target `(V7/III)`) per p.112(2) — deceptive when the third degree does not follow (p.114).

A dominant-seventh chord that matches NONE of the special functions and has NO functional
resolution SHALL NOT fall through to a repose function by degree position: a real tritone is
never tonic by position (the sole exception is the blues `I7`, p.112(3)). When such a chord's
root sits on the sixth, third, or flat-third degree (`VI7`, `III7`, `bIII7`), the analyzer
SHALL classify it as a **secondary dominant resolved deceptively** (`Dsec`, expected target
`(V7/x)` a perfect fourth above the root) — per Chediak p.114(1), when the expected diatonic
resolution does not happen the analysis remains that of a dominant, noted by its expectation.
This deceptive fallback SHALL apply only after every special-function and resolution branch
has failed, so no currently-classified chord changes label.

The **documented special functions** (quadro p.113: `I7`→blues tonic, `IV7`→blues
subdominant, `bVII7`/`bVI7`→minor subdominant `Emp`, `II7`→altered subdominant) are cited
facts, NOT curation suspects: the tritone curation ledger (baseline and persistence view)
SHALL exempt them, so the residual ledger contains only genuinely unadjudicated readings.

#### Scenario: bVII7 is a minor subdominant, not a secondary dominant
- **WHEN** in C major the chord `Bb7` resolves up a whole step to `C`
- **THEN** it is classified as a minor-subdominant / modal-interchange chord (`bVII7`)
- **AND** it is NOT labeled a secondary dominant

#### Scenario: bVII7 with a diatonic fourth-up resolution is a secondary dominant
- **WHEN** in A minor the chord `G7` (bVII7) resolves to `C` (the diatonic third degree)
- **THEN** it is classified `Dsec` (`V7/III`), not `Emp` — resolution precedes borrowing

#### Scenario: Blues sevenths on I and IV are not secondary dominants
- **WHEN** in C major `C7` (`I7`) and `F7` (`IV7`) appear in a blues context
- **THEN** each is classified as a blues chord, not a secondary dominant

#### Scenario: VII7 resolving to the tonic is cadential
- **WHEN** in C major a long `B7` resolves directly to `C` and is not preceded by a ii cadential
- **THEN** it is classified as a cadential `VII7`
- **AND** a short `B7` in the `F#m7 B7` cliché is classified as `V7/III` instead

#### Scenario: VII7 without tonic resolution reads as V7/III
- **WHEN** in C major a `B7` is followed by neither `C` nor its diatonic target
- **THEN** it is classified `Dsec` with expected target `(V7/III)` (p.112(2), deceptive p.114)

#### Scenario: II7 is an altered subdominant
- **WHEN** in C major a `D7` matches no dominant branch (e.g. followed by `C7M`)
- **THEN** it is classified `SD` as "Subdominante alterada (II7)" (quadro p.113)

#### Scenario: A genuine secondary dominant is still detected
- **WHEN** in C major `E7` resolves to `Am`
- **THEN** it remains a secondary dominant targeting the sixth degree (`V7/vi`)

#### Scenario: A deceptive VI7 is a secondary dominant, never tonic
- **WHEN** in C major an `A7` (`VI7`) does not resolve to any functional target (e.g. it is
  followed by `C7M` or ends the piece)
- **THEN** it is classified `Dsec` as a deceptively-resolved secondary dominant with expected
  target `(V7/II)` (Chediak p.114)
- **AND** it is never classified as tonic (`T`) by its degree position

#### Scenario: A deceptive III7 is a secondary dominant, never tonic
- **WHEN** in C major an `E7` (`III7`) is followed by a chord other than its diatonic target
- **THEN** it is classified `Dsec` with expected target `(V7/VI)` — not `T`

#### Scenario: Documented special functions are exempt from the curation ledger
- **WHEN** the tritone curation ledger is computed (baseline or persistence view)
- **THEN** occurrences reading as blues `I7` (`T`, degree I), blues `IV7` (`SD`, degree IV),
  minor subdominant (`Emp`), or altered subdominant `II7` (`SD`, degree II) are exempt with
  their citation (quadro p.113)
- **AND** the residual ledger contains only unadjudicated readings

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

