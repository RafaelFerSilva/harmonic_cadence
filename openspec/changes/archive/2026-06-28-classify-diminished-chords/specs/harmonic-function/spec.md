## ADDED Requirements

### Requirement: Non-dominant diminished chords are classified by type, not as modal borrowing

The analyzer SHALL classify a diminished-seventh chord that does NOT function as a rootless dominant (i.e. does not resolve a semitone above its written root) by its **type**, per Chediak (Vol. I, XXI–XXII, pp.102–104), rather than labeling it a modal borrowing. The types are determined by the motion of the diminished chord's root relative to its neighbors:

- **Auxiliary** (bordadura): the chord before and the chord after the diminished chord are the **same** chord (the diminished chord leaves a chord and returns to it).
- **Descending**: the next chord's root is a **semitone below** the diminished chord's root.
- **Passing / generic**: any other connective diminished chord that is neither a rootless dominant nor one of the above.

A diminished chord SHALL NOT be reported as a modal-borrowing (`Emp`) chord, because a modal borrowing is a major/minor diatonic chord of a parallel mode, never a diminished chord. The ascending diminished that resolves a semitone up (a rootless `V7(b9)`) keeps its dominant classification (unchanged), and the diatonic `vii°7` keeps its existing reading.

#### Scenario: A descending diminished is classified as descending, not modal borrowing
- **WHEN** in C major the chord `Ab°7` is followed by `G` (the diminished root descends a semitone)
- **THEN** it is classified as a descending diminished chord
- **AND** it is NOT labeled a modal borrowing (`Emp`)

#### Scenario: An auxiliary diminished (returning to the same chord) is classified as auxiliary
- **WHEN** the chord before and after a diminished chord are the same chord (e.g. `C  C#°7  C`, or `Dm  D#°7  Dm`)
- **THEN** the diminished chord is classified as an auxiliary (neighbor) diminished
- **AND** it is NOT labeled a modal borrowing (`Emp`)

#### Scenario: The ascending dominant diminished is unchanged
- **WHEN** a diminished chord resolves a semitone above its root (e.g. `C#°7 → Dm`)
- **THEN** it keeps its rootless-dominant classification (`V7(b9)/x`) and is NOT reclassified as auxiliary, descending, or passing

#### Scenario: A diminished chord is never reported as a modal borrowing
- **WHEN** any diminished-seventh chord is classified
- **THEN** its reported function is never `Emp` (modal borrowing)
