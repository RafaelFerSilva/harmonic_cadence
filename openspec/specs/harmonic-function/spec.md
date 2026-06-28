# harmonic-function Specification

## Purpose
TBD - created by archiving change functional-analysis. Update Purpose after archive.
## Requirements
### Requirement: Diatonic functional classification

The analyzer SHALL classify each diatonic degree into one of three tonal functions — tonic, subdominant, or dominant — by scale-degree position: `I`, `III`, `VI` are tonic; `II`, `IV` are subdominant; `V`, `VII` are dominant. This follows Chediak's degree–function table (Vol. I, p. 96) and the function definitions (p. 91).

#### Scenario: Major tonic degrees
- **WHEN** in C major the chords `C` (I), `Em` (III), and `Am` (VI) are classified
- **THEN** each is assigned the tonic function

#### Scenario: Major subdominant degrees
- **WHEN** in C major the chords `F` (IV) and `Dm` (II) are classified
- **THEN** each is assigned the subdominant function

#### Scenario: Major dominant degrees
- **WHEN** in C major the chords `G7` (V) and `Bm7(b5)` (VII) are classified
- **THEN** each is assigned the dominant function

### Requirement: Functional strength

The analyzer SHALL qualify each functional degree with a strength — strong, medium, or weak — per Chediak (p. 92): the principal degrees `I`, `IV`, `V` are strong; the substitutes `II` and `VII` are medium; the substitutes `III` and `VI` are weak.

#### Scenario: Principal degrees are strong
- **WHEN** the strength of degrees `I`, `IV`, `V` is queried
- **THEN** each is strong

#### Scenario: Substitutes of the subdominant and dominant are medium
- **WHEN** the strength of degrees `II` and `VII` is queried
- **THEN** each is medium

#### Scenario: Substitutes of the tonic are weak
- **WHEN** the strength of degrees `III` and `VI` is queried
- **THEN** each is weak

### Requirement: Minor-key diatonic field spans three scales

For a minor key, the analyzer SHALL treat a chord as diatonic when it belongs to the diatonic field of any of the three minor scales — harmonic, natural, or real melodic minor — per Chediak (pp. 94–96). The natural-minor `Vm7` MUST NOT be classified as a dominant (it has no tonal function).

#### Scenario: A chord diatonic to any minor scale is diatonic to the key
- **WHEN** the key is C minor
- **THEN** `G7` (harmonic/melodic `V7`), `Gm7` (natural `Vm7`), and `Bb7` (natural `bVII7`) are all diatonic to the key

#### Scenario: Natural-minor minor-five has no dominant function
- **WHEN** in C minor the chord `Gm7` (`Vm7`) is classified
- **THEN** it is NOT assigned the dominant function

#### Scenario: Minor tonic family
- **WHEN** in C minor the chord `Cm7` (or `Cm(7M)`, degree `Im`) is classified
- **THEN** it is assigned the tonic function

### Requirement: Diminished sevenths acting as rootless dominants carry dominant function

The analyzer SHALL assign the **dominant** function to a diminished-seventh chord that acts
as a rootless `V7(b9)` (i.e. resolves a semitone above its written root, per
applied-dominant-analysis), including when the chord is chromatic (non-diatonic to the key).
This extends the diatonic rule — under which `vii°7` already carries dominant function by
its degree (Chediak Vol. I p. 96) — to the chromatic ascending diminished chords
(`#i°7`, `#ii°7`, `#iv°7`) that function as secondary rootless dominants. A diminished
chord of approach/passing (one that does NOT resolve as a rootless dominant) SHALL NOT be
assigned dominant function.

#### Scenario: Diatonic vii°7 keeps its dominant function
- **WHEN** in C major `B°7` (degree `vii°7`) is classified
- **THEN** it is assigned the dominant function

#### Scenario: A chromatic ascending diminished acting as a secondary dominant is dominant
- **WHEN** in C major `C#°7` resolves to `Dm` (acting as `V7(b9)/ii`)
- **THEN** it is assigned the dominant function
- **AND** this holds even though `C#°7` is not diatonic to C major

#### Scenario: A passing diminished has no dominant function
- **WHEN** a diminished-seventh chord does not resolve a semitone above its root (a passing/auxiliary diminished)
- **THEN** it is NOT assigned the dominant function on that basis

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

