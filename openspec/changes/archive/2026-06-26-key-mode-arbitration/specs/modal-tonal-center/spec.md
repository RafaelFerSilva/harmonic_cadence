## ADDED Requirements

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
