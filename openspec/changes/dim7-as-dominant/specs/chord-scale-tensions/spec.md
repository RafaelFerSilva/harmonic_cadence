## ADDED Requirements

### Requirement: Diminished-seventh dominants map to the diminished chord-scale

A diminished-seventh chord that functions as a rootless dominant SHALL map to the
**diminished (octatonic) chord-scale** (per applied-dominant-analysis),
consistent with the existing flat-ninth-to-diminished mapping for spelled altered dominants (e.g.
`G7(b9)` already maps to the G diminished half-whole scale). The scale SHALL be the
octatonic collection that contains the chord's notes — equivalently, the diminished
(half-whole) scale of the implied dominant root (a major third below the written diminished
root). A diminished chord of approach/passing (no dominant function) keeps its current
treatment and is NOT given a dominant chord-scale on this basis.

#### Scenario: A vii°7 dominant maps to the diminished scale
- **WHEN** in C major `B°7` resolves to `C` (acting as the rootless dominant of I)
- **THEN** its recommended chord-scale is the diminished (octatonic) scale containing B-D-F-Ab
- **AND** this equals the diminished half-whole scale of the implied G dominant

#### Scenario: A secondary diminished dominant maps to the diminished scale
- **WHEN** in C major `C#°7` resolves to `Dm` (acting as `V7(b9)/ii`)
- **THEN** its recommended chord-scale is the diminished (octatonic) scale containing its notes

#### Scenario: A passing diminished is not given a dominant chord-scale
- **WHEN** a diminished-seventh chord does not function as a rootless dominant
- **THEN** it is NOT mapped to a dominant chord-scale by this requirement
