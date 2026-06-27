## ADDED Requirements

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
