# functional-analysis-baseline Specification

## Purpose
TBD - created by archiving change songbook-chediak-baseline. Update Purpose after archive.
## Requirements
### Requirement: Tonal center is established by Chediak's functional criterion, read from the music

The harness SHALL establish a piece's tonal center by Chediak's **functional-dominant criterion**
(Vol. I pp.84/87): a real-tritone dominant (a `Category.DOMINANT` V7 or SubV7) resolving by bass
to a **repose chord** in a structural/final position makes that chord the tonic. A **repose
chord** SHALL be precise: it MUST NOT itself be a real-tritone dominant (`Category` other than
`DOMINANT`), because the tonic reposes while the dominant is tension (Vol. I pp.84-85) — a V
resolving to another dominant is a secondary-dominant chain link (V/V→V), not a tonic arrival;
and its root MUST equal its bass, because the tonic reposes on its own root — an inverted chord
(e.g. `Fm/C`) is a non-tonic function, not the center. This SHALL be computed **from the chord
symbols alone**, with NO source key annotation as input. The function SHALL return the
Chediak-functional center (its pitch class and major/minor quality, taken from the resolved
repose chord) or `None` when no such functional resolution to a repose chord exists. The Cifra
Club `key` annotation SHALL NOT be consulted.

#### Scenario: The center is found from a functional-dominant resolution to a repose chord
- **WHEN** a progression contains a real-tritone V7/SubV7 resolving by bass to a repose chord (non-dominant, root == bass) in a structural/final position
- **THEN** the harness returns that repose chord's pitch class and quality as the Chediak-functional center
- **AND** it does so without reading any source key annotation

#### Scenario: A dominant-quality target does not establish a tonic
- **WHEN** a real-tritone dominant resolves by bass to a chord that is itself a real-tritone dominant (e.g. `A7(b9)→D7(13)`)
- **THEN** that target does NOT establish the tonic (it is a secondary-dominant chain link, not a repose)
- **AND** the criterion continues searching, returning `None` if no repose target anchors a structural extreme

#### Scenario: An inverted target does not establish a tonic
- **WHEN** a dominant resolves by bass to an inverted chord whose root differs from its bass (e.g. `G7(#5)→Fm/C`)
- **THEN** that target does NOT establish the tonic (the tonic reposes on its own root)
- **AND** the mode is never taken from a chord whose root differs from the candidate bass

#### Scenario: No functional resolution yields no center
- **WHEN** a progression has no real-tritone dominant resolving to a structural repose chord (e.g. a static modal vamp, or only resolutions to dominant/inverted targets)
- **THEN** the Chediak-functional center is `None`
- **AND** the song is quarantined from the center metric (its coverage is reported separately)

#### Scenario: The center is transposition-invariant
- **WHEN** the same piece is presented in two different transpositions
- **THEN** the Chediak-functional center maps by the same interval (the functional relationship is preserved)
- **AND** the agreement verdict against `detect_key` is unchanged

### Requirement: The center is reported as corroboration over a local songbook corpus, not a detector accuracy

The harness SHALL run over a **local songbook corpus** (`cifras/*.md`, ingested via
`cifra_from_text` / the local-chord-input path — never by scraping the Cifra Club) and report the
tonal center as **corroboration between two independent methods**: `detect_key` and the
Chediak-functional center. Because an annotation-free functional center is itself a heuristic (the
hard problem of identifying the tonic without an annotation), the harness SHALL NOT score
`detect_key` as "accurate/inaccurate" against it. Instead it SHALL report, over the subset where
the functional center fires: where the two methods **agree** (a high-confidence center) and where
they **disagree** (a **curation worklist** — songs a human/Chediak citation adjudicates). Songs
where the functional center does not fire SHALL be quarantined and counted separately so coverage
is never overstated. No source key annotation SHALL be consulted, and the verdicts SHALL be
invariant to each arrangement's transposition.

#### Scenario: Agreement between the two methods is a high-confidence center
- **WHEN** the Chediak-functional center fires and `detect_key` returns the same pitch class and mode
- **THEN** the song is reported as a corroborated (high-confidence) center
- **AND** no source key annotation is used in the verdict

#### Scenario: Disagreement goes to a curation worklist, not a detector score
- **WHEN** the functional center fires but `detect_key` returns a different center
- **THEN** the song is listed on the curation worklist with both centers visible
- **AND** it is NOT counted as a detector "miss" (neither method is asserted as gold)

#### Scenario: Coverage is reported honestly
- **WHEN** the baseline runs over the songbook
- **THEN** it reports how many songs the functional criterion fired on versus the total
- **AND** quarantined songs (no functional center) are counted separately

#### Scenario: The baseline never scrapes and never reads cc_key
- **WHEN** the baseline executes
- **THEN** it loads chords only from the local songbook files and never contacts the Cifra Club
- **AND** the Cifra Club `key` annotation is not read for anything

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

