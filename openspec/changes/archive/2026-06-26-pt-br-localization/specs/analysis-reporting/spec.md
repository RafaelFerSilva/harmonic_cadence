## ADDED Requirements

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
