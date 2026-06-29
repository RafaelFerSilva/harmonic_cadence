## ADDED Requirements

### Requirement: Extended dominants map to the Mixolydian chord-scale

The analyzer SHALL map an **extended dominant** to the **Mixolydian** chord-scale regardless of
its position relative to the key. An extended dominant is a dominant-seventh whose next chord is
itself a dominant-seventh a perfect fourth above (the cycle-of-fifths chain of Chediak Vol. I,
XXVIII(a), pp.107-108). Chediak states it explicitly (p.107, pointing to p.339): the extended
dominants take the Mixolydian mode as chord-scale. This rule SHALL take precedence over the
**position-based** dominant mapping (so an extended `II7`/`IV7`/`bVII7`, which the positional
rule would send to the Lydian-dominant scale, maps to Mixolydian), but SHALL NOT override the
**altered**-dominant mapping (an extended dominant carrying a real alteration keeps its altered
chord-scale, since the chord tones demand it).

#### Scenario: An extended II7 maps to Mixolydian, not Lydian-dominant
- **WHEN** in C major `D7` (a `II7`) is followed by `G7` (a dominant a perfect fourth above)
- **THEN** its recommended chord-scale is D Mixolydian
- **AND** NOT D Lydian-dominant (the position-based default for `II7`)

#### Scenario: A non-extended II7 keeps its position-based scale
- **WHEN** in C major `D7` is NOT followed by a dominant a perfect fourth above
- **THEN** its recommended chord-scale stays the position-based default (D Lydian-dominant)
