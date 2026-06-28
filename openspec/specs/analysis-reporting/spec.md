# analysis-reporting Specification

## Purpose

The system renders a completed harmonic analysis into reports (JSON, Markdown, HTML) that surface the depth and intelligence sections (tonal regions, modal analysis, Roman numerals, voice leading, chord-scales, the probabilistic functional parse, reharmonization suggestions, and the explanation), gracefully omits absent sections, and preserves the previously supported report sections.
## Requirements
### Requirement: Reports surface depth and intelligence sections

The generated reports (JSON, Markdown, HTML) SHALL render the analysis sections produced by the depth and intelligence layers when present in the result: **dominant tonal regions** (post-processed via `dominant_regions`), modal analysis, **modal coloring** (the piece-level overlay summarizing modal borrowings), Roman numerals, voice leading, chord-scales, the probabilistic functional parse, reharmonization suggestions, and the explanation.

The `tonal_regions` field in the result SHALL contain the output of `dominant_regions` (2–4 structurally meaningful regions) rather than the raw `segment_keys` windows. Raw segmentation data is not exposed in the public result.

When a `modal_coloring` annotation is present, the Markdown and HTML reports SHALL render it as a descriptive line subordinate to the tonal analysis (e.g. "Coloração modal: traços mixolídios"), never as a replacement of the key/mode heading.

#### Scenario: JSON report includes the depth and intelligence sections

- **WHEN** a successful analysis containing depth and intelligence sections is rendered as JSON
- **THEN** the JSON report contains the Roman numerals, modal analysis (when present), voice leading, chord-scales, functional parse, reharmonizations, and the explanation
- **AND** these are structured (serializable) values, not free text dumps of internal keys

#### Scenario: Modal coloring is rendered when present

- **WHEN** an analysis whose `modal_coloring` is present is rendered
- **THEN** the report includes a modal-coloring line describing the flavor and its evidence
- **AND** the key/mode heading still reflects the tonal reading (the coloring does not replace it)

#### Scenario: tonal_regions reflects dominant regions, not raw windows

- **WHEN** a modulating piece (e.g. Chega de Saudade) is analysed
- **THEN** `tonal_regions` in the result contains 2–4 entries representing the structurally dominant tonal areas
- **AND** it does NOT contain the raw 8-chord windows from `segment_keys` directly

#### Scenario: Single-key piece still reports one region

- **WHEN** a monotonal piece is analysed
- **THEN** `tonal_regions` contains exactly one region spanning the whole sequence
- **AND** the region's key matches the detected key from `detect_key`

#### Scenario: Markdown report renders the explanation and reharmonizations

- **WHEN** an analysis is rendered as Markdown
- **THEN** the report includes the explanation prose
- **AND** it lists the reharmonization suggestions with their technique and rationale
- **AND** it shows the Roman-numeral analysis

#### Scenario: HTML report includes the new sections

- **WHEN** an analysis is rendered as HTML
- **THEN** the HTML contains the explanation and at least the Roman numerals and reharmonization sections

### Requirement: Graceful omission of absent sections

A report SHALL omit any analysis section that is absent, `None`, or empty, and MUST remain valid output without errors.

#### Scenario: Tonal piece without modal analysis

- **WHEN** a tonal piece (whose `modal_analysis` is `None`) is rendered in any format
- **THEN** the modal-analysis section is omitted
- **AND** the report is produced successfully

#### Scenario: Tonal piece without modal coloring

- **WHEN** a tonal piece whose `modal_coloring` is `None` is rendered in any format
- **THEN** the modal-coloring line is omitted
- **AND** the report is produced successfully

#### Scenario: No reharmonization suggestions

- **WHEN** an analysis yields an empty reharmonization list
- **THEN** the reharmonization section is omitted (or shown as empty) without error

### Requirement: Existing report sections are preserved

The reports SHALL keep rendering the previously supported sections unchanged: the key/mode, statistics, the per-chord harmonic-analysis table, cadences, and the cifra lines.

#### Scenario: Backward-compatible rendering

- **WHEN** a report is generated after this change
- **THEN** the statistics, the per-chord harmonic analysis, and the cadences sections are still present
- **AND** no previously rendered section is removed or renamed

### Requirement: Reports present harmonic terms in Brazilian Portuguese

The reports SHALL present harmonic terms to the reader in Brazilian Portuguese — the key quality (major→maior, minor→menor), the church modes (e.g. phrygian→frígio, mixolydian→mixolídio), the chord qualities (e.g. dominant→dominante, diminished→diminuto, half-diminished→meio-diminuto), and the chord-scale names (e.g. mixolydian→mixolídio, lydian_dominant→lídio b7) — while keeping the chord letter names (A–G, the Brazilian cifra convention) and the internal model in canonical English. Translation happens at the presentation boundary only.

#### Scenario: Key quality is shown in Portuguese
- **WHEN** a piece analyzed as D minor is rendered
- **THEN** the report shows the key as "D menor" (the letter `D` kept, the quality translated)
- **AND** never "D minor"

#### Scenario: Church mode is shown in Portuguese
- **WHEN** the active mode is phrygian on D
- **THEN** the modal center is shown as "D frígio"

#### Scenario: Chord quality and chord-scale are shown in Portuguese
- **WHEN** a dominant chord with a G mixolydian chord-scale is rendered
- **THEN** the quality is shown as "dominante" and the scale as "G mixolídio"

