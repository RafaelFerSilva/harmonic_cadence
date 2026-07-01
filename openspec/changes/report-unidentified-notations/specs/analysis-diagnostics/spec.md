## ADDED Requirements

### Requirement: Unidentified chord-position notations are surfaced as diagnostics

The analyzer SHALL surface a **malformed chord** notation (a chord-position token that is not
parseable, per `chord-line-classification`) as visible degradation. Such a notation SHALL be
recorded in the result's `diagnostics` list, naming the unidentified token and aggregating by token
with an occurrence count; it MUST NOT be silently dropped and MUST NOT be replaced by a guessed
chord. The analysis SHALL still succeed using the valid chords, so a malformed notation degrades
that one token and not the whole song. A song with no malformed notation SHALL add nothing to
`diagnostics` on this account.

#### Scenario: A malformed notation is recorded in diagnostics
- **WHEN** a song's cifra contains a malformed chord notation (e.g. `D9/S`, an invalid `/S` bass)
- **THEN** the analysis succeeds using the valid chords
- **AND** the `diagnostics` list contains an entry naming the unidentified notation (`D9/S`) and how many times it occurred
- **AND** no guessed chord (e.g. `D9`) is fabricated from it

#### Scenario: A clean cifra adds no unidentified-notation diagnostic
- **WHEN** every chord-position token in the cifra parses to a valid chord
- **THEN** no unidentified-notation entry is added to `diagnostics`
