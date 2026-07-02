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

