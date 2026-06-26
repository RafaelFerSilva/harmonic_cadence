## MODIFIED Requirements

### Requirement: Chord realization into pitch classes

`cifra_core` SHALL realize a chord symbol into its set of pitch classes (root, third, fifth, any seventh/tensions, and the slash bass when present), so analysis can reason about chord tones rather than the raw symbol string. Realization MUST be tonality-independent and MUST be **derived from the structured parse** (one engine), so that the named category and the pitch classes never disagree.

#### Scenario: Major seventh chord realizes to four tones
- **WHEN** `"Cmaj7"` is realized
- **THEN** the pitch-class set equals that of `{C, E, G, B}`

#### Scenario: Half-diminished realizes correctly
- **WHEN** `"Dm7b5"` is realized
- **THEN** the pitch-class set equals that of `{D, F, Ab, C}`

#### Scenario: Brazilian 7M notation is a major seventh
- **WHEN** `"C7M"` is realized
- **THEN** it equals the realization of `"Cmaj7"`

#### Scenario: Bare diminished symbol is a diminished seventh
- **WHEN** `"C°"` (or `"Cdim"`) is realized
- **THEN** the pitch-class set equals that of `{C, Eb, Gb, A}` (a four-note diminished seventh)
- **AND** it equals the realization of `"Cdim7"`

#### Scenario: Suspended chords omit the third
- **WHEN** `"Csus4"` (or `"C4"`) is realized
- **THEN** the pitch-class set equals that of `{C, F, G}` with no third
- **AND** `"Csus2"` realizes to `{C, D, G}`

#### Scenario: Altered ninth is not double-counted
- **WHEN** `"C7(#9)"` (or `"C7(9+)"`) is realized
- **THEN** the set contains the sharp ninth (`D#`) and does NOT contain the natural ninth (`D`)

#### Scenario: Bare odd extension implies the seventh
- **WHEN** `"G9"` or `"G13"` is realized
- **THEN** the set contains `F` (the dominant seventh)
- **AND** `"C6/9"` and `"Cadd9"` are realized WITHOUT a seventh

#### Scenario: Cifra Club ± alterations are honored
- **WHEN** `"Em7(5-)"` is realized
- **THEN** the pitch-class set equals that of `{E, G, Bb, D}` (a half-diminished chord)
- **AND** `"A7(13-)"` contains `F` (the flat thirteenth), not `F#`

#### Scenario: Slash bass joins the realized set
- **WHEN** `"C/Bb"` is realized
- **THEN** the set includes `Bb` (the bass), in addition to `C E G`

## ADDED Requirements

### Requirement: Structured chord parse

`cifra_core` SHALL provide a structured parse of a chord symbol into independent slots — root (a spelling-preserving `Note`), an optional slash bass (`Note`), a third in `{major, minor, sus2, sus4, omitted}`, a fifth in `{perfect, diminished, augmented}`, a seventh in `{none, minor, major, diminished}`, plus the sets of upper-structure tensions and added tones — from which pitch-class realization is derived. The named chord category MUST be derivable from the slots.

#### Scenario: Altered fifth and tension are distinct slots
- **WHEN** `"C7(#11)"` is parsed
- **THEN** the fifth slot is `perfect` AND a `#11` tension is present
- **AND** they are two distinct pitch classes

#### Scenario: Suspension occupies the third slot
- **WHEN** `"G7sus4"` (or `"G7(4)"`) is parsed
- **THEN** the third slot is `sus4` and the seventh slot is `minor` (a dominant 7sus4)
- **AND** the `4` is NOT recorded as a sharp-eleventh tension

#### Scenario: Added tone versus stacked extension
- **WHEN** `"C6"` is parsed
- **THEN** the seventh slot is `none` and `6` is an added tone
- **AND** `"C9"` is parsed with the seventh slot `minor`

#### Scenario: Category derives from slots
- **WHEN** the category of a parsed chord is computed
- **THEN** it is `dominant` exactly when the third is `major` and the seventh is `minor` (the 3M–7m tritone)
- **AND** `diminished` when third `minor`, fifth `diminished`, seventh `diminished`
- **AND** `major` / `minor` otherwise, per the third

#### Scenario: Bass is independent of chord membership
- **WHEN** `"C/Bb"` is parsed
- **THEN** the bass slot is `Bb` even though it is the chord's seventh
- **AND** `"C/G"` parses as a second inversion (fifth in the bass)

### Requirement: Chord-symbol notation dialects

`cifra_core` SHALL accept both the Chediak `#`/`b` accidental dialect and the Cifra Club `+`/`-` suffix dialect for chord-symbol alterations, normalizing them to one internal representation, and SHALL treat degree numbers that name the same scale degree as equivalent.

#### Scenario: Plus/minus equals sharp/flat
- **WHEN** `"C7(9-)"` is realized
- **THEN** it equals the realization of `"C7(b9)"`
- **AND** `"C7(5+)"` equals `"C7(#5)"`
- **AND** `"A7(13-)"` equals `"A7(b13)"`

#### Scenario: Degree-class equivalence
- **WHEN** alterations name the second/fourth/sixth above an existing seventh
- **THEN** `4` and `11` denote the same tone, `6` and `13` the same, and `2` and `9` the same

#### Scenario: Flat-second spelling of the flat ninth
- **WHEN** `"A7(2-/13-)"` is realized
- **THEN** it equals the realization of `"A7(b9/b13)"`

#### Scenario: Bare second is an added ninth, not a suspension
- **WHEN** a bare `2` appears without `sus` (e.g. `"B2"`)
- **THEN** it is normalized to an added ninth with the third retained, realizing to `{B, D#, F#, C#}`
- **AND** only an explicit `"Bsus2"` omits the third
