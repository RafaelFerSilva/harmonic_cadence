## ADDED Requirements

### Requirement: Dominant-region post-processing of segmentation output

The analyzer SHALL provide a `dominant_regions` function that post-processes the raw output of `segment_keys` into a reduced set of structurally meaningful regions by merging adjacent same-key fragments and eliminating regions whose chord count falls below a configurable percentage threshold of the total. The underlying `segment_keys` function and its window size SHALL remain unchanged.

#### Scenario: Small regions are absorbed into neighbours
- **WHEN** `dominant_regions` receives regions where one region spans fewer than `min_pct` of the total chords
- **THEN** that region is merged into the adjacent region of the same tonality (if one exists) or the adjacent region with the closest K-S score
- **AND** no region in the output spans fewer than `min_pct` of the total chords

#### Scenario: Adjacent same-key fragments are consolidated
- **WHEN** two adjacent regions carry the same key (same tonic and mode), as can happen when a segment boundary falls inside a tonal plateau
- **THEN** they are merged into a single region spanning both

#### Scenario: A piece with two clear tonal areas yields two regions
- **WHEN** `dominant_regions` processes a bimodal piece like Chega de Saudade (D minor intro + D major refrão)
- **THEN** the output contains exactly two dominant regions: one for D minor and one for D major
- **AND** each region spans at least `min_pct` of the total chords

#### Scenario: A single-key piece yields one region
- **WHEN** a chord sequence stays in one key throughout
- **THEN** `dominant_regions` returns a single region, same as `segment_keys`

#### Scenario: segment_keys is not modified
- **WHEN** `segment_keys` is called directly
- **THEN** its output is identical to before this change (window=8, no post-processing)
