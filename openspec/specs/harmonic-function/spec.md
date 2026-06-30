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

### Requirement: II cadential chord classified by its dominant's target

The analyzer SHALL recognize a **II cadential** chord (Chediak Vol. I, XIX, p.100): a **minor** chord separated from a dominant by an ascending perfect fourth (the dominant root five semitones above the minor chord's root), i.e. the `IIm` of a `IIm V7 → x` cadence. **The following dominant MUST actually RESOLVE to its target** — a II cadential prepares a dominant *function*, and a dominant functions only when it resolves down a perfect fifth to its target chord. Concretely, with the dominant at index `i+1` and `target = (dominant_root + 5) mod 12`, the chord at index `i+2` MUST have its root (or bass) equal to `target`; otherwise the dominant does not function as a dominant (it is a non-resolving blues `I7`/`IV7` or a non-resolving borrowed chord) and the preceding minor chord is **not** a II cadential — it keeps its ordinary functional reading. This resolution test is purely intervallic (transposition-invariant) and does not depend on the dominant's own function code, which the blues-position branch may color as `T`/`SD` before resolution is considered. When the precondition holds, the analyzer SHALL classify the II cadential by the **target of that dominant**:

- **Primary**: the dominant resolves to the **tonic** (`Dm7 G7 → C`).
- **Secondary**: the dominant resolves to a **diatonic degree** other than the tonic (`F#m7 B7 → Em`, the ii-V of the third degree). The target MAY itself be a dominant chain link (`Em7 A7 → D7`); the dominant still functions because it resolves down a fifth.
- **Auxiliary**: the dominant resolves to a **modal-interchange (borrowed) chord** — a non-diatonic target (`Cm7 F7 → Bb`, the ii-V of bVII).

The II cadential reading SHALL take precedence over labeling the minor chord by its plain diatonic function (`SD`) or — for the chromatic secondary/auxiliary cases — as a modal borrowing (`Emp`) or tonic (`T`). The classification mirrors the applied-dominant axis (secondary = diatonic target, auxiliary = borrowed target). Because chord sheets carry no metre, the detection uses the harmonic relation (minor chord followed by a dominant a perfect fourth above that resolves to its target), not Chediak's strong-beat criterion.

#### Scenario: Primary II cadential (ii-V-I)
- **WHEN** in C major `Dm7` is followed by `G7` whose target a fifth below is `C` (the tonic), and the chord after `G7` resolves to `C`
- **THEN** `Dm7` is classified as a primary II cadential

#### Scenario: Secondary II cadential preparing a diatonic degree
- **WHEN** in C major `F#m7` is followed by `B7` whose target a fifth below is `E`, and the chord after `B7` resolves to `E`
- **THEN** `F#m7` is classified as a secondary II cadential (of `V7/III`)
- **AND** it is NOT labeled a modal borrowing (`Emp`)

#### Scenario: Secondary II cadential whose dominant resolves into another dominant
- **WHEN** `Em7` is followed by `A7` and the chord after `A7` is `D7` (root `D` = `A7`'s target), continuing a dominant chain
- **THEN** `Em7` is classified as a secondary II cadential (the `A7` functions as a dominant because it resolves down a fifth)

#### Scenario: Auxiliary II cadential preparing a borrowed chord
- **WHEN** in C major `Cm7` is followed by `F7` whose target a fifth below is `Bb`, and the chord after `F7` resolves to `Bb`
- **THEN** `Cm7` is classified as an auxiliary II cadential (of `V7/bVII`)
- **AND** it is NOT labeled tonic (`T`) or modal borrowing (`Emp`)

#### Scenario: A minor chord before a non-resolving dominant is not a II cadential
- **WHEN** `Dm7` is followed by `G7` (a fourth above) but the chord after `G7` is not `G7`'s target `C` (e.g. it loops back to `Dm7`, as when `G7` is a static blues `I7`)
- **THEN** `Dm7` is NOT classified as a II cadential (its dominant does not resolve, so it does not function as a dominant)
- **AND** `Dm7` keeps its ordinary functional reading

#### Scenario: A minor chord not followed by a fourth-above dominant is not a II cadential
- **WHEN** a minor chord is not followed by a dominant-seventh a perfect fourth above its root
- **THEN** it is NOT classified as a II cadential and keeps its ordinary functional reading

### Requirement: Extended dominant resolving into another dominant

The analyzer SHALL recognize an **extended dominant** (Chediak Vol. I, XXVIII(a),
pp.107-108): a dominant-seventh chord whose **next chord is itself a dominant-seventh** a
**perfect fourth above** (next root five semitones above), i.e. a dominant that resolves
into another dominant around the cycle of fifths. Because such a chord resolves into another
dominant rather than into a degree of the key, it belongs to the **chain, not the
tonality**: the analyzer SHALL classify it with the dedicated function code `Dext` and
SHALL NOT label it a secondary dominant (`Dsec`, `V7/x`) tied to a scale degree. Its
chord-scale is the **mixolydian** mode (Chediak: extended dominants take the mixolydian
chord-scale). Only the chord that **reconnects** to the tonality at the end of the chain
(its target is a diatonic degree or the tonic) resumes ordinary degree-bound reading
(`Dsec`/`D`).

The extended-dominant reading SHALL take precedence over the secondary-dominant (`Dsec`)
reading, since the two are distinguished precisely by the **quality of the target**: a
diatonic/borrowed resolution target keeps `Dsec`/`Daux`, a **dominant** resolution target a
perfect fourth above makes the chord extended (`Dext`).

Note: the SubV-extended chain (dominants separated by a **descending semitone**, Chediak
XXVIII c/d) is out of scope for this requirement — a local semitone pair is ambiguous
against the blues IV7→III7 reading and needs chromatic-chain detection (a separate change).

#### Scenario: Extended dominant resolving up a fourth into another dominant
- **WHEN** in C major `A7` is followed by `D7` (also a dominant, root a perfect fourth above)
- **THEN** `A7` is classified as an extended dominant (`Dext`)
- **AND** it is NOT classified as a secondary dominant `V7/II`

#### Scenario: Chain of extended dominants
- **WHEN** in C major the run `A7 D7 G7` precedes `C` (each dominant resolving into the next)
- **THEN** `A7` and `D7` are each classified as extended dominants (`Dext`)
- **AND** `G7`, whose target a fifth below is the tonic `C`, keeps its ordinary dominant reading (`D`)

#### Scenario: Extended dominant takes the mixolydian chord-scale
- **WHEN** a dominant is classified as an extended dominant (`Dext`)
- **THEN** its recommended chord-scale is the mixolydian mode

#### Scenario: A dominant resolving into a diatonic degree is not extended
- **WHEN** in C major `E7` resolves to `Am` (a diatonic degree, not a dominant)
- **THEN** `E7` keeps its secondary-dominant reading (`Dsec`, `V7/vi`) and is NOT `Dext`

### Requirement: Extended SubV chain detected over the full progression

The analyzer SHALL recognize an **extended SubV** (Chediak Vol. I, XXVIII c/d, pp.107-108): a
dominant-seventh that, as a member of a **chain**, resolves into another dominant-seventh a
**descending semitone** below. Because a single local semitone pair is ambiguous against the
blues `IV7→III7` reading and chromatic passing dominants, the analyzer SHALL classify a chord
as an extended SubV ONLY when it belongs to a **maximal run of consecutive dominant-sevenths
descending by semitone of length ≥ 3 chords** (≥ 2 semitone motions), computed over the whole
progression — not from a local pair. Each member of such a run that resolves into another
dominant SHALL be classified with the function code `Dext` (the extended-SubV flavor in its
name). The **terminal** chord of the run — one that resolves a semitone into a **non-dominant**
(e.g. `Db7 → C`, a SubV of the tonic) — SHALL NOT be extended and keeps its ordinary reading
(primary `SubV`). This chain reading SHALL take precedence over the blues `I7`/`IV7` reading
for confirmed chain members. The mapping mirrors the perfect-fourth extended dominant (`Dext`),
differing only in the connecting interval (descending semitone instead of ascending fourth).

#### Scenario: A descending-semitone chain of dominants is read as extended SubVs
- **WHEN** in C major the run `F#7 F7 E7 Eb7 D7 Db7` precedes `C` (each dominant resolving a semitone below into the next)
- **THEN** `F#7`, `F7`, `E7`, `Eb7`, and `D7` are each classified as extended (`Dext`)
- **AND** `Db7`, which resolves a semitone into the non-dominant tonic `C`, keeps its primary `SubV` reading

#### Scenario: A chain member overrides the blues IV7 reading
- **WHEN** `F7` (a `IV7`) is a member of a confirmed descending-semitone chain
- **THEN** `F7` is classified as an extended SubV (`Dext`), NOT as `SD` blues

#### Scenario: An isolated semitone pair is not a chain
- **WHEN** in C major `F7` is followed by `E7` with no further descending-semitone dominant on either side (a length-2 pair)
- **THEN** `F7` is NOT classified as an extended SubV and keeps its blues `SD` reading
- **AND** the pair does NOT form an extended-SubV chain

#### Scenario: Chain requires consecutive dominants
- **WHEN** a semitone-descending step lands on a non-dominant chord (breaking the run)
- **THEN** the run ends there and only dominant members within a length-≥3 run are extended

