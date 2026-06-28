## MODIFIED Requirements

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
