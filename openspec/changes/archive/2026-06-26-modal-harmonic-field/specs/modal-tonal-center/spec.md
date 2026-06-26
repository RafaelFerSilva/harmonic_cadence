## ADDED Requirements

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
