## ADDED Requirements

### Requirement: Extended dominant resolving into another dominant

The analyzer SHALL recognize an **extended dominant** (Chediak Vol. I, XXVIII(a),
pp.107-108): a dominant-seventh chord whose **next chord is itself a dominant-seventh** a
**perfect fourth above** (next root five semitones above), i.e. a dominant that resolves
into another dominant around the cycle of fifths. Because such a chord resolves into another
dominant rather than into a degree of the key, it belongs to the **chain, not the
tonality**: the analyzer SHALL classify it with the dedicated function code `Dext` and
SHALL NOT label it a secondary dominant (`Dsec`, `V7/x`) tied to a scale degree. Its
chord-scale is the **mixolydian** mode (Chediak: extended dominants take the mixolydian
chord-scale). Only the chord that **reconnects** to the tonality at the end of the chain
(its target is a diatonic degree or the tonic) resumes ordinary degree-bound reading
(`Dsec`/`D`).

The extended-dominant reading SHALL take precedence over the secondary-dominant (`Dsec`)
reading, since the two are distinguished precisely by the **quality of the target**: a
diatonic/borrowed resolution target keeps `Dsec`/`Daux`, a **dominant** resolution target a
perfect fourth above makes the chord extended (`Dext`).

Note: the SubV-extended chain (dominants separated by a **descending semitone**, Chediak
XXVIII c/d) is out of scope for this requirement — a local semitone pair is ambiguous
against the blues IV7→III7 reading and needs chromatic-chain detection (a separate change).

#### Scenario: Extended dominant resolving up a fourth into another dominant
- **WHEN** in C major `A7` is followed by `D7` (also a dominant, root a perfect fourth above)
- **THEN** `A7` is classified as an extended dominant (`Dext`)
- **AND** it is NOT classified as a secondary dominant `V7/II`

#### Scenario: Chain of extended dominants
- **WHEN** in C major the run `A7 D7 G7` precedes `C` (each dominant resolving into the next)
- **THEN** `A7` and `D7` are each classified as extended dominants (`Dext`)
- **AND** `G7`, whose target a fifth below is the tonic `C`, keeps its ordinary dominant reading (`D`)

#### Scenario: Extended dominant takes the mixolydian chord-scale
- **WHEN** a dominant is classified as an extended dominant (`Dext`)
- **THEN** its recommended chord-scale is the mixolydian mode

#### Scenario: A dominant resolving into a diatonic degree is not extended
- **WHEN** in C major `E7` resolves to `Am` (a diatonic degree, not a dominant)
- **THEN** `E7` keeps its secondary-dominant reading (`Dsec`, `V7/vi`) and is NOT `Dext`
