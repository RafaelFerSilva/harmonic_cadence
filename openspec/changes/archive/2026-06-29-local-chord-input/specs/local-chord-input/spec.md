## ADDED Requirements

### Requirement: Analyze harmony from a local chord source, independent of the Cifra Club

The system SHALL accept a **local chord source** — a `.txt` file or a raw chord string — and
produce the same harmonic analysis it produces for a scraped song, without contacting the Cifra
Club or any network provider. The local source SHALL be ingested into the same normalized
internal representation (`Cifra`/data) the `SongProvider` produces and run through the **unchanged**
`AnalysisService`. The key SHALL be detected from the chords alone (`detect_key`); no source `Tom:`
annotation is read, because a local source carries none.

#### Scenario: A local chord file is analyzed end to end
- **WHEN** a user supplies a local file of chord lines
- **THEN** the system produces the full harmonic analysis (key, mode, degrees, functions, cadences, modal coloring, reports) from the chords
- **AND** it does so without any network call to the Cifra Club

#### Scenario: The key comes from the chords, not a source annotation
- **WHEN** a local source is analyzed
- **THEN** the reported key is the one detected by `detect_key` over the chords
- **AND** no `Tom:`/source-key field is consulted (none exists for a local source)

#### Scenario: The analytic core is unchanged
- **WHEN** the same chord sequence is analyzed via a local source and via a scraped song
- **THEN** the detected key, degrees, functions, cadences, and modal coloring are identical
- **AND** `detect_key`, the quality gate / functional travas, and `modal_coloring` are not modified by this capability

### Requirement: Local ingestion reuses the canonical normalization exactly once

Local ingestion SHALL convert raw text into clean cifra lines using the canonical, idempotent
filter (`cifra_core.clean_cifra_lines`) applied **once**, so a local source reaches the engine in
the identical shape a scraped page does. Ingestion SHALL NOT introduce a parallel chord parser or
line filter; chord extraction remains the engine's responsibility (`ChordPattern`). Ingestion
SHALL produce only normalized lines plus optional identity (artist/title), never an analytic
verdict. Optional `artist`/`title` metadata MAY be supplied; when absent the engine's existing
"unknown" fallback applies. The produced representation SHALL carry an empty source key.

#### Scenario: Raw text is normalized through the shared filter
- **WHEN** raw chord text containing noise lines (tabs, section markers, blank lines) is ingested
- **THEN** the noise is removed by `clean_cifra_lines` and the chord lines are preserved
- **AND** no second filtering pass is applied downstream (the filter is idempotent and applied once)

#### Scenario: Identity defaults when not provided
- **WHEN** a local source is ingested without artist/title
- **THEN** ingestion succeeds and the analysis uses the engine's default "unknown" identity
- **AND** the produced representation has an empty source key

### Requirement: A CLI entry analyzes a local file with visible degradation

The CLI SHALL provide a command to analyze a local chord file, wired to the same analysis service
and report generation as the scrape path, but built **without** a network provider (no scraping,
no cache lookup). The command SHALL accept optional artist/title metadata and the existing report
format options. Failures — file missing, empty file, or no valid chords — SHALL be reported with a
clear message and a non-zero exit status, never a silent or empty success.

#### Scenario: Analyzing a valid local file produces a report
- **WHEN** the user runs the local-file analysis command on a file of valid chords
- **THEN** a report is generated in the requested format(s) via the existing report factory
- **AND** no network provider is constructed or contacted

#### Scenario: A missing or empty file fails visibly
- **WHEN** the file does not exist, is empty, or contains no recognizable chords
- **THEN** the command prints a clear error and exits non-zero
- **AND** it does not emit an empty or misleading report

#### Scenario: The scrape path is unaffected
- **WHEN** the existing `analyze <artist> <song>` scrape command is run
- **THEN** its behavior and output are byte-identical to before this capability was added
