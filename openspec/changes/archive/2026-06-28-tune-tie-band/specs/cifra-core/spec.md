## MODIFIED Requirements

### Requirement: Single source of truth for cifra line preprocessing

The `cifra-core` package SHALL own cifra line cleaning/filtering (tablature, section/structural markers, tuning/instrument lines, blank and consecutive-duplicate lines), exposing one canonical filter consumed by both packages. Line filtering MUST happen in exactly one place in the end-to-end pipeline, and MUST preserve the relative order of the lines it keeps.

#### Scenario: Filtering is not duplicated end-to-end
- **WHEN** a cifra travels from scrape to analysis
- **THEN** tablature/section filtering is applied once according to the documented contract
- **AND** the analyzer does not re-run a second, divergent filter over already-filtered lines

#### Scenario: Filtering is idempotent
- **WHEN** the canonical filter is applied to already-filtered lines
- **THEN** the output equals the input (no further lines are removed or altered)

#### Scenario: Tablature lines are removed
- **WHEN** the input contains guitar-tab lines (e.g. `E|---0---2---`, `B|--1--1--`)
- **THEN** those lines are absent from the output

#### Scenario: Section and structural markers are removed
- **WHEN** the input contains markers such as `[Intro]`, `Parte 1 de 2`, or `tom: C`
- **THEN** those lines are absent from the output

#### Scenario: Instrument tuning lines are removed
- **WHEN** the input contains a tuning line (e.g. `"Afinação Drop D: D A D G B E"`, `"Capotraste na 2ª casa"`)
- **THEN** that line is absent from the output
- **AND** the single-letter note names within it are NOT extracted as chord symbols

#### Scenario: Chord and lyric content is kept in order
- **WHEN** the input mixes chord lines and lyric lines with tablature between them
- **THEN** the chord and lyric lines are retained in their original relative order

#### Scenario: Consecutive duplicate lines are collapsed
- **WHEN** the input contains the same line repeated on adjacent rows
- **THEN** only a single occurrence is kept
