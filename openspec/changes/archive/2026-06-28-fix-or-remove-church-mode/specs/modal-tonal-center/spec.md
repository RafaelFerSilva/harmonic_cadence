## MODIFIED Requirements

### Requirement: Modal classification of a tonal center

The analyzer SHALL provide modal classification (ionian, dorian, phrygian, lydian, mixolydian, aeolian, locrian) as a **library function** that, given a clean diatonic pitch-class collection and a tonic, identifies the mode. This classification SHALL NOT be applied automatically to promote the tonal center of an analyzed song: deriving a mode from the full pitch-class collection of a real song is unreliable (the union of every chord's pitches is near-chromatic, and the permissive phrygian branch fires on ordinary minor pieces — empirically 12/60 spurious phrygian on the validation corpus). The pipeline SHALL NOT emit a modal-analysis section from automatic detection; the tonal reading from `detect_key` prevails. Reintroducing automatic modal detection is deferred to a future change that supplies a curated modal corpus and a principled modal-vs-tonal discriminator.

#### Scenario: Mixolydian is recognized by its flat seventh (library)
- **WHEN** the modal classifier is called on a clean progression centered on G that uses the G-major collection but with `F` natural and no `F#` leading tone (e.g. `G F C G`)
- **THEN** it returns G mixolydian

#### Scenario: Dorian is recognized by its raised sixth (library)
- **WHEN** the modal classifier is called on a clean minor-centered progression on D that uses `B` natural (raised sixth) consistently (e.g. `Dm G Dm Em`)
- **THEN** it returns D dorian

#### Scenario: Ambiguous tonal pieces are not classified as a mode
- **WHEN** the classifier sees a progression with the leading tone and standard dominant function (e.g. `C F G7 C`)
- **THEN** it returns no mode (None)

#### Scenario: A real analyzed song is not auto-promoted to a mode
- **WHEN** a full song is analyzed through the pipeline
- **THEN** no modal-analysis section is produced by automatic modal detection
- **AND** the song's key and mode are the tonal reading from `detect_key`

### Requirement: Characteristic cadential and avoided chords per mode

When a mode is given, the library SHALL expose the mode's characteristic cadential chords and its avoided chords, per Chediak (Vol. I, pp. 122-125), alongside the mode's characteristic note. These are the source's curated selection (which chords firm up the modal flavor in a cadence, and which pull back to major/minor tonality), not a derivation of the diatonic field.

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

#### Scenario: The library exposes the selection for a given mode
- **WHEN** the cadential and avoided chords of a mode are queried
- **THEN** the characteristic note, the cadential chords, and the avoided chords for that mode are returned

## REMOVED Requirements

### Requirement: A mode refines, never overrides, the detected key

**Reason:** This requirement specified the arbitration gate (`_mode_refines_key`) that guarded the automatic promotion of a detected mode into the analysis. The promotion is being removed because it produced false positives (12/60 spurious phrygian labels on the validation corpus, catching zero genuine modes). With no automatic promotion, there is nothing to gate.

**Migration:** The tonal reading from `detect_key` now prevails unconditionally — there is no modal override to reject. The protections this requirement encoded are subsumed: a slash-chord ending (e.g. `D/A` in A major) is read correctly by `detect_key` alone (no modal path can misread it), and a quality-flipping mode can no longer be applied because no mode is applied at all. The "tonal center from the most prominent bass" estimation remains as internal behavior of the `detect_mode` library function (`_central_pc`), unchanged, for the future modal-detection change to build on.
