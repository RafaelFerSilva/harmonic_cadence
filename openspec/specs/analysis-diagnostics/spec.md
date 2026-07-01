# analysis-diagnostics Specification

## Purpose
TBD - created by archiving change pipeline-observability. Update Purpose after archive.
## Requirements
### Requirement: Optional analysis sections degrade visibly, not silently

The analyzer's optional sections (modal analysis, roman numerals, voice leading, chord-scales, functional parse, reharmonizations, explanation, tonal regions) SHALL degrade gracefully on error — yielding their empty/None default rather than failing the whole analysis — but the degradation MUST be observable: the error is logged and recorded in a `diagnostics` list on the result (section name + error), so an empty value caused by an exception is distinguishable from "nothing applies". A successful analysis exposes an empty `diagnostics` list.

#### Scenario: A clean analysis reports no diagnostics
- **WHEN** an analysis completes with every section computed
- **THEN** the result's `diagnostics` list is empty

#### Scenario: A section that errors is recorded, not swallowed
- **WHEN** one optional section raises during analysis
- **THEN** that section's value is its empty default
- **AND** the rest of the analysis still succeeds
- **AND** the `diagnostics` list contains an entry naming that section and its error

#### Scenario: Structured diagnostics are exposed in the JSON report
- **WHEN** the analysis is rendered as JSON
- **THEN** the `diagnostics` are present in the output

### Requirement: Unidentified chord-position notations are surfaced as diagnostics

The analyzer SHALL surface a **malformed chord** notation (a chord-position token that is not
parseable, per `chord-line-classification`) as visible degradation. Such a notation SHALL be
recorded in the result's `diagnostics` list, naming the unidentified token and aggregating by token
with an occurrence count; it MUST NOT be silently dropped and MUST NOT be replaced by a guessed
chord. The analysis SHALL still succeed using the valid chords, so a malformed notation degrades
that one token and not the whole song. A song with no malformed notation SHALL add nothing to
`diagnostics` on this account.

#### Scenario: A malformed notation is recorded in diagnostics
- **WHEN** a song's cifra contains a malformed chord notation (e.g. `D9/S`, an invalid `/S` bass)
- **THEN** the analysis succeeds using the valid chords
- **AND** the `diagnostics` list contains an entry naming the unidentified notation (`D9/S`) and how many times it occurred
- **AND** no guessed chord (e.g. `D9`) is fabricated from it

#### Scenario: A clean cifra adds no unidentified-notation diagnostic
- **WHEN** every chord-position token in the cifra parses to a valid chord
- **THEN** no unidentified-notation entry is added to `diagnostics`

