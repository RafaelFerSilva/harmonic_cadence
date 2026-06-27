# modal-tonal-center Specification

## Purpose

The analyzer classifies the active church mode of a tonal center from the diatonic pitch-class collection and the tonic, computes degrees and characteristic chords relative to the modal tonic, and recognizes the characteristic modal cadences — rather than forcing every piece into major or minor.
## Requirements
### Requirement: Modal classification of a tonal center

The analyzer SHALL classify the active mode (ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian) of a tonal center from the diatonic pitch-class collection and the tonic, rather than forcing every piece into major or minor.

#### Scenario: Mixolydian is recognized by its flat seventh
- **WHEN** a progression centered on G uses the G-major collection but with `F` natural and no `F#` leading tone (e.g. `G F C G`)
- **THEN** the mode is classified as G mixolydian

#### Scenario: Dorian is recognized by its raised sixth
- **WHEN** a minor-centered progression on D uses `B` natural (raised sixth) consistently (e.g. `Dm G Dm Em`)
- **THEN** the mode is classified as D dorian

#### Scenario: Ambiguous tonal pieces remain major/minor
- **WHEN** a progression has the leading tone and standard dominant function (e.g. `C F G7 C`)
- **THEN** it is classified as major/minor, not as a mode

### Requirement: Modal degrees and characteristic chords are diatonic to the mode

When a mode is active, the analyzer SHALL compute degrees relative to the modal tonic and treat the mode's characteristic chords as diatonic — NOT as modal borrowing.

#### Scenario: bVII in mixolydian is a diatonic degree, not a borrowing
- **WHEN** the active mode is G mixolydian and the chord `F` appears
- **THEN** `F` is reported as the diatonic `bVII` of the mode
- **AND** it is NOT labeled as modal borrowing (`Emp`)

#### Scenario: Characteristic chord of the mode is identified
- **WHEN** the active mode is D dorian and the major `IV` (`G`) appears
- **THEN** it is identified as the characteristic chord of the mode

### Requirement: Modal cadences

The analyzer SHALL recognize the characteristic modal cadences (at least bVII–I for mixolydian, bII–I for phrygian, and the minor v–i / IV–i shapes) distinct from the tonal authentic/plagal cadences.

#### Scenario: Mixolydian cadence bVII-I
- **WHEN** in G mixolydian the progression `F G` (bVII–I) occurs
- **THEN** a mixolydian cadence is reported
- **AND** it is not misreported as a tonal authentic cadence

#### Scenario: Phrygian cadence bII-I
- **WHEN** in E phrygian the progression `F E` (bII–I) occurs
- **THEN** a phrygian cadence is reported

### Requirement: Modal harmonic field

When a mode is active, the analyzer SHALL expose the mode's diatonic harmonic field — its seven diatonic chords as (degree, quality) pairs — **derived from the modal scale** (so it is correct by construction), matching Chediak's modal tables (Vol. I, pp. 122-125). The analyzer SHALL also expose each mode's characteristic note.

#### Scenario: Dorian field matches the source
- **WHEN** the harmonic field of D dorian is computed
- **THEN** its tetrads are `Dm7, Em7, F7M, G7, Am7, Bm7(b5), C7M`
- **AND** they correspond to degrees `Im7, IIm7, bIII7M, IV7, Vm7, VIm7(b5), bVII7M`

#### Scenario: Mixolydian field matches the source
- **WHEN** the harmonic field of G mixolydian is computed
- **THEN** its tetrads are `G7, Am7, Bm7(b5), C7M, Dm7, Em7, F7M`

#### Scenario: Phrygian seventh degree is minor, not dominant
- **WHEN** the harmonic field of E phrygian is computed
- **THEN** its seventh degree `bVII` is a minor seventh (`Dm7`), not a dominant seventh

#### Scenario: Characteristic note per mode
- **WHEN** the characteristic note of a mode is queried
- **THEN** dorian is the natural sixth, phrygian the flat second, lydian the sharp fourth, mixolydian the flat seventh, aeolian the flat sixth, and locrian the flat second and flat sixth

### Requirement: Characteristic cadential and avoided chords per mode

When a mode is active, the analyzer SHALL expose the mode's characteristic cadential chords and its avoided chords, per Chediak (Vol. I, pp. 122-125), alongside the mode's characteristic note. These are the source's curated selection (which chords firm up the modal flavor in a cadence, and which pull back to major/minor tonality), not a derivation of the diatonic field.

#### Scenario: Dorian cadential and avoided chords
- **WHEN** the active mode is dorian
- **THEN** the cadential chords are `IIm7`, `IV7`, `bVII7M`
- **AND** the avoided chord is `VIm7(b5)`

#### Scenario: Mixolydian cadential and avoided chords
- **WHEN** the active mode is mixolydian
- **THEN** the cadential chords are `I7`, `Vm7`, `bVII7M`
- **AND** the avoided chord is `IIIm7(b5)`

#### Scenario: Phrygian cadential and avoided chords
- **WHEN** the active mode is phrygian
- **THEN** the cadential chords are `bII7M`, `bVIIm7`
- **AND** the avoided chords include `Vm7(b5)` and `bIII7`

#### Scenario: The active modal section exposes the selection
- **WHEN** a piece with an active mode is analyzed
- **THEN** its modal analysis section reports the characteristic note, the cadential chords, and the avoided chords

### Requirement: A mode refines, never overrides, the detected key

A church mode SHALL be applied to a piece only when it **refines** the key from `detect_key` — i.e., it shares the same tonic AND the same major/minor quality. A mode that disagrees on the tonic, or flips the major/minor quality, SHALL be rejected as tonal chromaticism, and the tonal reading from `detect_key` prevails. When a mode is rejected, the modal analysis section MUST also be absent (no key/mode contradiction in the output). The modal tonal center SHALL be estimated from the most prominent bass (the pedal/finalis), not from the root of the final chord.

#### Scenario: A tonal piece ending on a slash chord is not misread as a mode on the slash root
- **WHEN** a piece in A major rests on an `A` pedal and ends on `D/A` (D over the A bass)
- **THEN** its key is reported as A major
- **AND** it is NOT reported as D minor or a D mode (the tonal center is the bass A, not the root D)

#### Scenario: A mode that flips the quality is rejected
- **WHEN** `detect_key` reports D major and a mode classifier suggests D phrygian (a minor mode) from incidental chromaticism
- **THEN** the piece stays D major
- **AND** no modal analysis section is reported

#### Scenario: A mode that agrees in tonic and quality is accepted as a refinement
- **WHEN** `detect_key` reports A minor and the mode classifier reports A phrygian (same tonic, both minor)
- **THEN** the piece is refined to A phrygian

### Requirement: Modal harmonic field has a single canonical implementation

The modal harmonic field and the modal-borrowing description SHALL be provided by
a single canonical implementation. The codebase MUST NOT contain an orphan or
duplicate module that re-implements these routines from the legacy hardcoded
mode-harmony tables. This preserves the existing "derived, correct by
construction" guarantee (Chediak Vol. I, pp. 122-125) as the only source of truth,
and removes the risk of edits diverging between a live copy and a dead one.

This requirement adds a structural (single-source-of-truth) guarantee only; it does
not change any observable analysis output. The derived modal harmonic field and the
modal-borrowing descriptions behave exactly as before.

#### Scenario: No orphan duplicate of the modal-field routines

- **WHEN** the codebase is inspected for implementations of the modal harmonic
  field, modal-borrowing description, scale transposition, and note normalization
- **THEN** each routine has exactly one implementation reachable from the live
  pipeline
- **AND** there is no orphan module (importable but unimported) duplicating them

#### Scenario: Derived modal field is unchanged by the cleanup

- **WHEN** the harmonic field of any mode is computed after the dead-code removal
- **THEN** it matches the result before the removal (degrees and tetrad qualities
  identical), confirming behavior was preserved

### Requirement: Modal borrowing description preserves enharmonic spelling

The modal-borrowing description and the derived modal harmonic field SHALL render
note names with correct enharmonic spelling for the tonality, using the
spelling-preserving `Note` model — flats MUST NOT be collapsed into sharps. A
flat-key context renders `Bb`, `Eb`, `Ab` (never `A#`, `D#`, `G#`), matching
Chediak's per-key spelling (Vol. I; e.g. F major contains `Bb`). This brings the
borrowing description into conformance with the `music-theory-core` spelling rule.

The multi-origin nature of the description is preserved: when a borrowed chord could
come from more than one parallel mode, all candidate origins are still listed — only
the note spelling changes.

#### Scenario: Borrowed chord in a flat key spells with flats

- **WHEN** the modal origin of a chord borrowed in a flat-spelled key (e.g. F major)
  is described
- **THEN** the rendered scale and harmonic field use flat spellings (`Bb`, `Eb`, …)
- **AND** no note in the output is rendered as a sharp where the key calls for a flat

#### Scenario: Multiple parallel-mode origins are still reported

- **WHEN** a borrowed chord is diatonic to more than one parallel mode
- **THEN** the description lists each candidate origin (as before)
- **AND** only the note spelling differs from the legacy output, not the set of
  origins

### Requirement: Modal harmonic field is derived, not hardcoded

The modal harmonic field exposed for borrowing description SHALL be derived from the
spelled scale (`build_scale` + stacked-tetrad quality), not read from a hardcoded
mode-harmony table. The derived field MUST match Chediak's modal tables
(Vol. I, pp. 122-125).

#### Scenario: Derived field matches the source tables

- **WHEN** the harmonic field used in a borrowing description is computed for a mode
- **THEN** its (degree, quality) pairs are derived from the mode's scale
- **AND** they match the corresponding Chediak modal table

