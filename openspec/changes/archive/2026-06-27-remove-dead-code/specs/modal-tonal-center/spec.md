## ADDED Requirements

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
