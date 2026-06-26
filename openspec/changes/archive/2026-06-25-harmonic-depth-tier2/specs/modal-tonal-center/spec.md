## ADDED Requirements

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
