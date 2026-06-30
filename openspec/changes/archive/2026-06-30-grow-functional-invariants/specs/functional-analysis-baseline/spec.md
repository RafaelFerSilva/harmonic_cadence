## MODIFIED Requirements

### Requirement: The baseline asserts Chediak functional invariants, invariant to transposition

The harness SHALL validate, per song, a set of **hard functional invariants** — defects that
must not occur — independent of the center and invariant to transposition. The hard invariants
gated as defects are: (a) a real-tritone `Category.DOMINANT` chord SHALL be read with a dominant
function code (primary `V7`, secondary `Dsec`, `Daux`, extended `Dext`, or `SubV`), never as
modal interchange or a plain subdominant; and (b) a `Category.DIMINISHED` chord SHALL be
classified only as a dominant (`D`/`Dsec` — `vii°7` is a rootless `V7(b9)`, p.90) or as a
non-dominant diminished (`Dim` — auxiliary/descending/passing, XXI-XXII), **never** as modal
interchange (`Emp`), subdominant (`SD`), tonic (`T`), or modal function. Violations of (a) or (b)
SHALL be reported as functional-analysis defects, per song, like the existing tritone check.

The engine SHALL continue to **recognize** ii-V motion (emitting the `D2` ii-cadential code,
XIX) and to **tag** cadences within the five-cadence taxonomy (XXXII); the baseline reports these
as produced. However, the **coherence** between those subsystems and the function coder — that a
`D2` is followed by a chord whose FUNCTION is dominant, and that a cadence tagged `V→I` has a
dominant-function V and a tonic-function I — is a KNOWN, MEASURED incoherence (the `D2` code keys
off the next chord's quality, not its function; cadence tagging keys off degree, not function
code) and SHALL NOT yet be gated as a defect. These coherence invariants are deferred to separate
fix changes so the baseline gate stays green.

#### Scenario: A real tritone is always read as a dominant
- **WHEN** a chord is a real-tritone `Category.DOMINANT`
- **THEN** the analysis classifies it as a dominant by its resolution target (primary/secondary/SubV/auxiliary/extended), never as modal interchange or a plain subdominant
- **AND** a violation is reported as a functional defect

#### Scenario: A diminished chord is never read as modal interchange, subdominant, or tonic
- **WHEN** a chord is a `Category.DIMINISHED`
- **THEN** its function code is one of `D`/`Dsec` (dominant, rootless `V7(b9)`) or `Dim` (auxiliary/descending/passing)
- **AND** it is never `Emp`, `SD`, `T`, or a modal function
- **AND** a violation is reported as a functional defect

#### Scenario: ii-V recognition and cadence tagging are produced but coherence is not yet gated
- **WHEN** the baseline runs over the songbook
- **THEN** the engine still emits `D2` for ii-cadential motion and populates the five-cadence taxonomy
- **AND** the baseline does NOT report a defect when a `D2`'s target or a cadence's target carries a non-dominant/non-tonic function code (these incoherences are measured and deferred to fix changes)

#### Scenario: Invariants hold under transposition
- **WHEN** a song is analyzed in two transpositions
- **THEN** the hard functional-invariant verdicts (dominant classification, diminished classification) are identical
- **AND** the absolute key does not change any functional verdict
