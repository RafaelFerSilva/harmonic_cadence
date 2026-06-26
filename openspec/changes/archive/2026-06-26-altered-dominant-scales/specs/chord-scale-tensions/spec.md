## ADDED Requirements

### Requirement: Altered dominants map to their altered chord-scale

An altered dominant-seventh chord SHALL map to its altered chord-scale per Chediak (Vol. I, pp. 349-352), and this mapping SHALL take precedence over the position-based dominant mapping. A flat fifth or sharp eleventh maps to the lydian-dominant scale; a sharp fifth maps to the whole-tone scale; a flat ninth maps to the diminished (half-whole) scale; a sharp ninth (or a combined flat-and-sharp ninth) maps to the altered scale. A dominant with no such alteration keeps its position-based scale.

#### Scenario: Flat-ninth dominant maps to the diminished scale
- **WHEN** in C major the chord `G7(b9)` is analyzed
- **THEN** its recommended chord-scale is the G diminished (half-whole) scale

#### Scenario: Sharp-ninth dominant maps to the altered scale
- **WHEN** `G7(#9)` is analyzed
- **THEN** its recommended chord-scale is the G altered scale

#### Scenario: Sharp-fifth dominant maps to the whole-tone scale
- **WHEN** `G7(#5)` is analyzed
- **THEN** its recommended chord-scale is the G whole-tone scale

#### Scenario: Flat-fifth or sharp-eleventh dominant maps to lydian dominant
- **WHEN** `G7(b5)` or `G7(#11)` is analyzed
- **THEN** its recommended chord-scale is the G lydian-dominant scale

#### Scenario: ± dialect alterations are honored
- **WHEN** `G7(9-)` (Cifra Club notation) is analyzed
- **THEN** its recommended chord-scale equals that of `G7(b9)`

#### Scenario: An unaltered dominant keeps its position-based scale
- **WHEN** a plain `G7` (V) is analyzed in C major
- **THEN** its recommended chord-scale remains G Mixolydian
