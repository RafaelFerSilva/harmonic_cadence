## MODIFIED Requirements

### Requirement: The baseline asserts Chediak functional invariants, invariant to transposition

The harness SHALL validate, per song, a set of **hard functional invariants** — defects that
must not occur — independent of the center and invariant to transposition. The hard invariants
gated as defects are: (a) a real-tritone `Category.DOMINANT` chord SHALL be read with a dominant
function code (primary `V7`, secondary `Dsec`, `Daux`, extended `Dext`, or `SubV`), never as
modal interchange or a plain subdominant; (b) a `Category.DIMINISHED` chord SHALL be
classified only as a dominant (`D`/`Dsec` — `vii°7` is a rootless `V7(b9)`, p.90) or as a
non-dominant diminished (`Dim` — auxiliary/descending/passing, XXI-XXII), **never** as modal
interchange (`Emp`), subdominant (`SD`), tonic (`T`), or modal function; (c) every chord coded
`D2` (ii-cadential, XIX) SHALL have its prepared dominant **resolve to its target** (the chord
two positions later drops to `(V_root + 5) mod 12` by root or bass); and (d) every cadence of the
**authentic/plagal family** (perfect, imperfect, plagal, authentic — those that resolve to the
tonic, XXXII) SHALL have a target chord whose **function code is a repose (tonic) function**,
never a dominant family (`D`/`D2`/`Dsec`/`Daux`/`Dext`), tritone-substitute (`SubV`/`Sub2`), or
diminished (`Dim`) code — a cadence is the combination of functions `D` and `T` (p.110), so a
V→I whose "I" functions as a dominant is a direct resolution (XXXIII), not a cadence. Violations
of (a), (b), (c), or (d) SHALL be reported as functional-analysis defects, per song, like the
existing tritone check, and each gate SHALL be born GREEN (an already-violated invariant is a bug
report, not a gate).

The engine SHALL continue to **recognize** ii-V motion (emitting the `D2` ii-cadential code,
XIX) and to **tag** cadences within the five-cadence taxonomy (XXXII); the baseline reports these
as produced. The **coherence** between those subsystems and the function coder is **no longer
deferred**: the `D2` resolution coherence (c) and the cadence-to-tonic function coherence (d) are
gated invariants, both transposition-invariant (keyed off function and intervallic resolution, not
the absolute key).

#### Scenario: A real tritone is always read as a dominant
- **WHEN** a chord is a real-tritone `Category.DOMINANT`
- **THEN** the analysis classifies it as a dominant by its resolution target (primary/secondary/SubV/auxiliary/extended), never as modal interchange or a plain subdominant
- **AND** a violation is reported as a functional defect

#### Scenario: A diminished chord is never read as modal interchange, subdominant, or tonic
- **WHEN** a chord is a `Category.DIMINISHED`
- **THEN** its function code is one of `D`/`Dsec` (dominant, rootless `V7(b9)`) or `Dim` (auxiliary/descending/passing)
- **AND** it is never `Emp`, `SD`, `T`, or a modal function
- **AND** a violation is reported as a functional defect

#### Scenario: Every D2 resolves to its target
- **WHEN** a chord is coded `D2` (ii-cadential) at index `i`
- **THEN** `chords[i]` is minor, `chords[i+1]` is a dominant-seventh a perfect fourth above, and `chords[i+2]` resolves to `(chords[i+1].root + 5) mod 12` by root or bass
- **AND** a violation (a `D2` whose dominant does not resolve) is reported as a functional defect

#### Scenario: Every authentic/plagal cadence resolves to a tonic-function target
- **WHEN** a perfect, imperfect, plagal, or authentic cadence is reported (a cadence resolving to the tonic)
- **THEN** the target chord's function code is a repose (tonic) function, never `D`/`D2`/`Dsec`/`Daux`/`Dext`/`SubV`/`Sub2`/`Dim`
- **AND** a violation (a cadence whose "I" functions as a dominant or diminished) is reported as a functional defect

#### Scenario: Invariants hold under transposition
- **WHEN** a song is analyzed in two transpositions
- **THEN** the hard functional-invariant verdicts (dominant classification, diminished classification, D2 resolution, cadence-to-tonic coherence) are identical
- **AND** the absolute key does not change any functional verdict
