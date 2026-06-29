## MODIFIED Requirements

### Requirement: Applied-chord notation

The analyzer SHALL notate applied chords using slash notation `V7/x` (and `vii°/x`),
consistent with `applied-dominant-analysis` — **except** for an **extended dominant** or an
**extended SubV**, neither of which carries an applied numeral (Chediak: "the extended
dominants do not take the roman numeral"; their sound is not directly bound to the tonality):

- an **extended dominant** is a dominant-seventh whose next chord is itself a dominant-seventh
  a **perfect fourth above** (the cycle-of-fifths chain of Chediak XXVIII(a), pp.107-108);
- an **extended SubV** is a dominant-seventh that is a member of a descending-semitone chain
  of dominants (length ≥ 3), resolving a semitone into another dominant (Chediak XXVIII c/d).

For either case the analytical figure is the plain chord symbol; the resolution is conveyed by
the arrow, not by a degree tied to the key. Only a dominant whose target is a key degree
(diatonic or the tonic), and which is not a chain member, retains the `V7/x` applied notation.

#### Scenario: Secondary dominant numeral
- **WHEN** in C major `E7` resolves to `Am`
- **THEN** its numeral is `V7/vi`

#### Scenario: Extended dominant carries no applied numeral
- **WHEN** in C major `A7` resolves into `D7` (itself a dominant a perfect fourth above)
- **THEN** `A7` does NOT get the applied numeral `V7/II`
- **AND** its analytical figure is the plain dominant symbol

#### Scenario: Extended SubV carries no applied numeral
- **WHEN** in C major `Eb7` is a member of a descending-semitone chain resolving into `D7`
- **THEN** `Eb7` does NOT get an applied numeral
- **AND** its analytical figure is the plain chord symbol
