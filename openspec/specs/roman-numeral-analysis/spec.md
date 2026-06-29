# roman-numeral-analysis Specification

## Purpose

The analyzer produces quality-aware Roman numerals for each chord, reflecting scale degree, chord quality, seventh suffixes, inversion figures derived from the bass, and applied-chord slash notation.

## Requirements

### Requirement: Roman numeral with quality

The analyzer SHALL produce a Roman numeral for each chord reflecting its scale degree and quality: uppercase for major, lowercase for minor, `°` for diminished, `+` for augmented, with seventh/quality suffixes.

#### Scenario: Diatonic triads carry quality-aware numerals
- **WHEN** in C major the chords `C`, `Dm`, `Em`, `F`, `G`, `Am`, `Bdim` are analyzed
- **THEN** their numerals are `I`, `ii`, `iii`, `IV`, `V`, `vi`, `vii°`

#### Scenario: Seventh quality is reflected
- **WHEN** in C major the chord `G7` is analyzed
- **THEN** its numeral is `V7`
- **AND** `Cmaj7` is `Imaj7`

### Requirement: Inversion figures from the bass

The analyzer SHALL determine inversion from the chord's bass note and annotate the Roman numeral with figured-bass symbols: root position (none), first inversion `6`, second inversion `6/4`; for sevenths `6/5`, `4/3`, `4/2`.

#### Scenario: First inversion triad
- **WHEN** the chord `C/E` is analyzed in C major
- **THEN** its numeral is `I6` (first inversion)

#### Scenario: Second inversion triad
- **WHEN** the chord `C/G` is analyzed in C major
- **THEN** its numeral is `I6/4`

#### Scenario: Seventh chord first inversion
- **WHEN** the chord `G7/B` is analyzed in C major
- **THEN** its numeral is `V6/5`

#### Scenario: Root position has no figure
- **WHEN** the chord `G7` (root in the bass) is analyzed
- **THEN** its numeral carries no inversion figure

### Requirement: Applied-chord notation

The analyzer SHALL notate applied chords using slash notation `V7/x` (and `vii°/x`),
consistent with `applied-dominant-analysis` — **except** for an **extended dominant**: a
dominant-seventh whose next chord is **itself a dominant-seventh a perfect fourth above**
(the cycle-of-fifths chain of Chediak XXVIII(a), pp.107-108). An extended dominant SHALL NOT
carry an applied numeral (`V7/x`), because — in Chediak's words — "the extended dominants do
not take the roman numeral" (their sound is not directly bound to the tonality). Its
analytical figure is the plain chord symbol; the resolution is conveyed by the arrow, not by
a degree tied to the key. Only a dominant whose target is a key degree (diatonic or the
tonic) retains the `V7/x` applied notation.

#### Scenario: Secondary dominant numeral
- **WHEN** in C major `E7` resolves to `Am`
- **THEN** its numeral is `V7/vi`

#### Scenario: Extended dominant carries no applied numeral
- **WHEN** in C major `A7` resolves into `D7` (itself a dominant a perfect fourth above)
- **THEN** `A7` does NOT get the applied numeral `V7/II`
- **AND** its analytical figure is the plain dominant symbol
