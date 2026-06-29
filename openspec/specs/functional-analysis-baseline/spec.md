# functional-analysis-baseline Specification

## Purpose
TBD - created by archiving change songbook-chediak-baseline. Update Purpose after archive.
## Requirements
### Requirement: Tonal center is established by Chediak's functional criterion, read from the music

The harness SHALL establish a piece's tonal center by Chediak's **functional-dominant criterion**
(Vol. I pp.84/87): a real-tritone dominant (a `Category.DOMINANT` V7 or SubV7) resolving by bass
to a repose chord in a structural/final position makes that chord the tonic. This SHALL be
computed **from the chord symbols alone**, with NO source key annotation as input. The function
SHALL return the Chediak-functional center (its pitch class and major/minor quality, taken from
the resolved tonic chord) or `None` when no such functional resolution exists. The Cifra Club
`key` annotation SHALL NOT be consulted.

#### Scenario: The center is found from a functional-dominant resolution
- **WHEN** a progression contains a real-tritone V7/SubV7 resolving by bass to a repose chord in a structural/final position
- **THEN** the harness returns that chord's pitch class and quality as the Chediak-functional center
- **AND** it does so without reading any source key annotation

#### Scenario: No functional resolution yields no center
- **WHEN** a progression has no real-tritone dominant resolving to a structural repose chord (e.g. a static modal vamp)
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

The harness SHALL validate, per song, that the functional reading obeys Chediak's
classification rules — independent of the center and invariant to transposition:
a real-tritone dominant is classified as a dominant by its target (primary `V7→I`, secondary
`V7/x`, `SubV7`, auxiliary, extended; Vol. I XVIII-XIX, XXVIII); diminished chords are classified
by type (XXI-XXII) and `vii°7` reads as a dominant (p.90), never as modal interchange; ii-V
motion is recognized (XIX); cadences are tagged within the five-cadence taxonomy (XXXII).
Violations SHALL be reported as functional-analysis defects. These checks SHALL hold in any
transposition because they are degree- and quality-relative.

#### Scenario: A real tritone is always read as a dominant
- **WHEN** a chord is a real-tritone `Category.DOMINANT`
- **THEN** the analysis classifies it as a dominant by its resolution target (primary/secondary/SubV/auxiliary/extended), never as modal interchange or a plain subdominant
- **AND** a violation is reported as a functional defect

#### Scenario: Invariants hold under transposition
- **WHEN** a song is analyzed in two transpositions
- **THEN** the functional-invariant verdicts (dominant classification, diminished type, ii-V, cadence taxonomy) are identical
- **AND** the absolute key does not change any functional verdict

