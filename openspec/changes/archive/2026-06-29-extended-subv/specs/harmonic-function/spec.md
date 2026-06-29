## ADDED Requirements

### Requirement: Extended SubV chain detected over the full progression

The analyzer SHALL recognize an **extended SubV** (Chediak Vol. I, XXVIII c/d, pp.107-108): a
dominant-seventh that, as a member of a **chain**, resolves into another dominant-seventh a
**descending semitone** below. Because a single local semitone pair is ambiguous against the
blues `IV7→III7` reading and chromatic passing dominants, the analyzer SHALL classify a chord
as an extended SubV ONLY when it belongs to a **maximal run of consecutive dominant-sevenths
descending by semitone of length ≥ 3 chords** (≥ 2 semitone motions), computed over the whole
progression — not from a local pair. Each member of such a run that resolves into another
dominant SHALL be classified with the function code `Dext` (the extended-SubV flavor in its
name). The **terminal** chord of the run — one that resolves a semitone into a **non-dominant**
(e.g. `Db7 → C`, a SubV of the tonic) — SHALL NOT be extended and keeps its ordinary reading
(primary `SubV`). This chain reading SHALL take precedence over the blues `I7`/`IV7` reading
for confirmed chain members. The mapping mirrors the perfect-fourth extended dominant (`Dext`),
differing only in the connecting interval (descending semitone instead of ascending fourth).

#### Scenario: A descending-semitone chain of dominants is read as extended SubVs
- **WHEN** in C major the run `F#7 F7 E7 Eb7 D7 Db7` precedes `C` (each dominant resolving a semitone below into the next)
- **THEN** `F#7`, `F7`, `E7`, `Eb7`, and `D7` are each classified as extended (`Dext`)
- **AND** `Db7`, which resolves a semitone into the non-dominant tonic `C`, keeps its primary `SubV` reading

#### Scenario: A chain member overrides the blues IV7 reading
- **WHEN** `F7` (a `IV7`) is a member of a confirmed descending-semitone chain
- **THEN** `F7` is classified as an extended SubV (`Dext`), NOT as `SD` blues

#### Scenario: An isolated semitone pair is not a chain
- **WHEN** in C major `F7` is followed by `E7` with no further descending-semitone dominant on either side (a length-2 pair)
- **THEN** `F7` is NOT classified as an extended SubV and keeps its blues `SD` reading
- **AND** the pair does NOT form an extended-SubV chain

#### Scenario: Chain requires consecutive dominants
- **WHEN** a semitone-descending step lands on a non-dominant chord (breaking the run)
- **THEN** the run ends there and only dominant members within a length-≥3 run are extended
