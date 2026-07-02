## MODIFIED Requirements

### Requirement: The baseline asserts Chediak functional invariants, invariant to transposition

The harness SHALL validate, per song, a set of **hard functional invariants** — defects that
must not occur — independent of the center and invariant to transposition, and SHALL separately
report a **curation ledger** for a check that is not a clean invariant on the corpus. The checks
SHALL actually execute (using the accessors the `Chord` type exposes — `.quality`,
`.properties.bass` — never a phantom `get_category()`/`.bass` whose `AttributeError` would be
swallowed).

The **hard gated invariants** (born GREEN; an already-violated invariant is a bug report, not a
gate) are: (a) a `Category.DIMINISHED` chord SHALL be classified only as a dominant (`D`/`Dsec` —
`vii°7` is a rootless `V7(b9)`, p.90) or as a non-dominant diminished (`Dim` —
auxiliary/descending/passing, XXI-XXII), **never** as modal interchange (`Emp`), subdominant
(`SD`), tonic (`T`), or modal function; (b) every chord coded `D2` (ii-cadential, XIX) SHALL have
its prepared dominant **resolve to its target** (the chord two positions later drops to
`(V_root + 5) mod 12` by root or bass); and (c) every cadence of the **authentic/plagal family**
(perfect, imperfect, plagal, authentic — those that resolve to the tonic, XXXII) SHALL have a
target chord whose **function code is a repose (tonic) function**, never a dominant family
(`D`/`D2`/`Dsec`/`Daux`/`Dext`), tritone-substitute (`SubV`/`Sub2`), or diminished (`Dim`) code.
Violations of (a), (b), or (c) SHALL be reported as functional-analysis defects, per song.

The **real-tritone reading** is NOT a hard gate. The invariant "a real-tritone
`Category.DOMINANT` chord is read as a dominant" has **documented exceptions in the corpus** — an
`I7` chord functioning as tonic (blues/funk, `i7-funk-anchor`) is a legitimate non-dominant
tritone. The harness SHALL therefore report real-tritone-non-dominant readings as a **curation
ledger** (a worklist to adjudicate against Chediak), **after exempting** the structurally-clean
legitimate class: a chord read as `T` whose degree is the tonic (`I`/`i`). The remaining ledger
entries (a real tritone read as `T` on a non-tonic degree, as `Emp`, or as `Outro`) SHALL be
reported as a worklist count, never as a green/failed gate, and their per-case adjudication is
out of scope until a citable authority resolves them.

The engine SHALL continue to **recognize** ii-V motion (emitting the `D2` ii-cadential code,
XIX) and to **tag** cadences within the five-cadence taxonomy (XXXII); the baseline reports these
as produced. The `D2` resolution coherence (b) and the cadence-to-tonic function coherence (c)
are gated invariants, both transposition-invariant.

#### Scenario: The tritone and diminished checks actually execute

- **WHEN** the baseline runs its functional checks over a song
- **THEN** each chord is evaluated using `Chord(sym).quality` (and `.properties.bass` for the D2
  resolution), so no check is silently skipped by an `AttributeError` on a non-existent accessor

#### Scenario: A diminished chord is never read as modal interchange, subdominant, or tonic

- **WHEN** a chord is a `Category.DIMINISHED`
- **THEN** its function code is one of `D`/`Dsec` (dominant, rootless `V7(b9)`) or `Dim`
  (auxiliary/descending/passing), never `Emp`, `SD`, `T`, or a modal function
- **AND** a violation is reported as a functional defect that fails the gate

#### Scenario: I7-as-tonic is exempt from the tritone ledger

- **WHEN** a real-tritone chord is read as `T` and its degree is the tonic (`I`/`i`)
- **THEN** it is a legitimate `I7`-as-tonic (blues/funk, `i7-funk-anchor`) and SHALL NOT appear
  in the tritone curation ledger

#### Scenario: Remaining real-tritone-non-dominant readings are a ledger, not a gate

- **WHEN** a real-tritone chord is read as `T` on a non-tonic degree, or as `Emp`, or as `Outro`
- **THEN** it is reported in the curation ledger as a worklist entry (`song`, `position`,
  `symbol`, `function_code`)
- **AND** it SHALL NOT be counted as a green or failed hard gate

#### Scenario: Every D2 resolves to its target

- **WHEN** a chord is coded `D2` (ii-cadential) at index `i`
- **THEN** `chords[i]` is minor, `chords[i+1]` is a dominant-seventh a perfect fourth above, and
  `chords[i+2]` resolves to `(chords[i+1].root + 5) mod 12` by root or bass (using
  `.properties.bass`)
- **AND** a violation is reported as a functional defect that fails the gate

#### Scenario: Every authentic/plagal cadence resolves to a tonic-function target

- **WHEN** a perfect, imperfect, plagal, or authentic cadence is reported
- **THEN** the target chord's function code is a repose (tonic) function, never
  `D`/`D2`/`Dsec`/`Daux`/`Dext`/`SubV`/`Sub2`/`Dim`
- **AND** a violation is reported as a functional defect that fails the gate

#### Scenario: Invariants hold under transposition

- **WHEN** a song is analyzed in two transpositions
- **THEN** the hard-gate verdicts (diminished, D2, cadence) and the tritone-ledger membership
  are identical, keyed off function/degree/intervallic resolution, not the absolute key
