## ADDED Requirements

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
