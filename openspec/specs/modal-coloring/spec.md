# modal-coloring Specification

## Purpose

A descriptive, piece-level overlay that summarizes the modal borrowings already present in a tonal-functional analysis into a single coloring flavor (mixolydian over a major key, phrygian over a minor key). The coloring is anchored to the tonic detected by `detect_key` and is strictly additive: it never alters the tonal-functional analysis (key, mode, scale degrees, harmonic functions, cadences, or per-chord borrowing labels), and it is absent by default for purely tonal pieces.

## Requirements

### Requirement: Modal coloring is a descriptive overlay anchored to the tonal key

The analyzer SHALL expose an optional `modal_coloring` annotation that summarizes, at the piece level, the modal borrowings already present in the tonal-functional analysis. The coloring SHALL be anchored to the tonic detected by `detect_key` and SHALL NOT alter the key, mode, scale degrees, harmonic functions, or cadence taxonomy — it is strictly additive and describes a coloring of an otherwise tonal piece. The coloring SHALL NOT re-estimate a tonal center; all characteristic degrees are computed relative to the already-detected tonal tonic.

#### Scenario: Coloring never changes the tonal reading
- **WHEN** a piece receives a modal-coloring annotation
- **THEN** its reported key, mode, scale degrees, harmonic functions, and cadences are exactly those of the tonal-functional analysis without the coloring
- **AND** the coloring appears only as an additional descriptive field

#### Scenario: Coloring is anchored to the detected tonic, not a re-estimated center
- **WHEN** an A-minor piece contains a `Bb` (bII) chord resolving to the A-minor tonic
- **THEN** the coloring is evaluated relative to the A tonal tonic (phrygian coloring)
- **AND** the tonal center is NOT re-estimated to Bb or any other root

### Requirement: Coloring triggers on key-mode-specific evidence, anchored and asymmetric

The analyzer SHALL emit at most one v1 coloring flavor, with mode-specific triggers (all relative to the tonal tonic), reflecting that the characteristic degrees are non-diatonic to the tonal mode:

- **Mixolydian (major keys only):** triggered by EITHER a `bVII→I` cadence, OR a recurrent (≥2) `bVII` major chord, OR a recurrent (≥2) minor-`v` chord. The minor `v` is included because Chediak gives I7/Vm7/bVII7M as the mode's cadential chords (Vol. I p. 124), and a minor dominant is non-diatonic to a major key (e.g. Upa Neguinho is Ré mixolídio via Vm7, with no bVII).
- **Phrygian (minor keys only):** triggered ONLY by a structural `bII→i` cadence occurring at least twice. A mere recurrent or single `bII` SHALL NOT trigger phrygian, because a `bII` in a minor key is usually a Neapolitan / tritone-sub dominant (already labeled "SubV"), not phrygian color.

Mixolydian SHALL NOT be emitted for a minor key (where `bVII` is the diatonic aeolian seventh). Dorian and any other mode SHALL NOT be emitted in v1 (dorian and mixolydian share a pitch collection, so distinguishing them requires modal-center detection, which is out of scope). A single passing alteration SHALL NOT trigger any coloring.

#### Scenario: Mixolydian coloring from a bVII-I cadence in a major key
- **WHEN** a major-key piece contains a `bVII` major chord resolving to the `I` (bVII→I)
- **THEN** a mixolydian coloring is emitted
- **AND** its evidence cites the bVII→I cadence

#### Scenario: Mixolydian coloring from a recurrent minor-v in a major key
- **WHEN** a major-key piece contains a minor-`v` chord at least twice and no leading-tone dominant role for it
- **THEN** a mixolydian coloring is emitted
- **AND** its evidence cites the minor-v borrowing

#### Scenario: bVII in a minor key does not trigger mixolydian
- **WHEN** a minor (aeolian) piece contains `bVII` major chords (its diatonic seventh)
- **THEN** no mixolydian coloring is emitted

#### Scenario: Phrygian coloring from a structural bII-i cadence in a minor key
- **WHEN** a minor-key piece contains the `bII→i` cadence at least twice
- **THEN** a phrygian coloring is emitted
- **AND** its evidence cites the recurrent bII→i cadence

#### Scenario: A single Neapolitan bII does not trigger phrygian
- **WHEN** a minor-key piece contains a single `bII` chord (or a `bII` that does not recur as a structural cadence to the tonic)
- **THEN** no phrygian coloring is emitted
- **AND** the chord is still labeled in the per-chord analysis (e.g. "SubV" or modal borrowing)

#### Scenario: Dorian is not emitted in v1
- **WHEN** a minor-key piece contains a major `IV` (the dorian raised sixth)
- **THEN** no dorian coloring is emitted in v1 (distinguishing dorian from mixolydian requires modal-center detection)

### Requirement: Coloring summarizes per-chord borrowings without replacing them

The per-chord modal-borrowing labels ("Emp") produced by the functional analysis SHALL be preserved unchanged. The `modal_coloring` annotation SHALL be a piece-level summary of those borrowings when they form a consistent modal pattern, never a replacement for the per-chord labels.

#### Scenario: Per-chord borrowing labels are unchanged by coloring
- **WHEN** a piece receives a mixolydian coloring from its bVII chords
- **THEN** each bVII chord is still individually labeled "Emp" (modal borrowing) in the per-chord analysis
- **AND** the coloring is an additional summary, not a relabeling

### Requirement: Coloring is absent by default for purely tonal pieces

The `modal_coloring` annotation SHALL be `None` (absent) for a piece whose borrowings do not form a triggering pattern, including ordinary minor (aeolian) pieces that merely contain incidental chromaticism. The analyzer MUST NOT emit a coloring for such pieces.

#### Scenario: An ordinary minor piece gets no coloring
- **WHEN** a tonal minor (aeolian) piece with incidental chromaticism but no characteristic modal cadence and no recurrent characteristic borrowing is analyzed
- **THEN** its `modal_coloring` is `None`

#### Scenario: A diatonic major piece gets no coloring
- **WHEN** a plainly diatonic major piece (e.g. `C F G7 C`) is analyzed
- **THEN** its `modal_coloring` is `None`
