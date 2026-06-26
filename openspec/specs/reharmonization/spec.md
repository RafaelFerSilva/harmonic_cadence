# reharmonization Specification

## Purpose

The analyzer produces idiomatic reharmonization suggestions for a progression, each carrying a technique label and a human-readable rationale while preserving the underlying harmonic function of the spot it changes.

## Requirements

### Requirement: Idiomatic reharmonization suggestions

The analyzer SHALL produce reharmonization suggestions for a progression using idiomatic techniques — at least tritone substitution, secondary-dominant insertion, ii–V interpolation, modal interchange, and diatonic substitution — each suggestion carrying a technique label and a human-readable rationale, and preserving the underlying harmonic function.

#### Scenario: Tritone substitution of a dominant
- **WHEN** a dominant `G7` resolves to `C`
- **THEN** a suggestion replaces `G7` with `Db7` labeled as a tritone substitution
- **AND** the rationale notes the shared guide-tone tritone

#### Scenario: Secondary-dominant insertion before a diatonic target
- **WHEN** a diatonic chord (e.g. `Dm`, the ii) is preceded by another chord
- **THEN** a suggestion inserts its secondary dominant (`A7`, `V7/ii`) before it
- **AND** the suggestion is labeled secondary-dominant insertion

#### Scenario: Suggestions are labeled and justified
- **WHEN** any reharmonization suggestion is produced
- **THEN** it includes the technique name, the affected position(s), the replacement/insertion, and a rationale

### Requirement: Function-preserving suggestions

Each reharmonization suggestion SHALL preserve the harmonic function of the spot it changes (e.g. a tritone sub keeps the dominant function; a diatonic substitution keeps the tonic/subdominant role).

#### Scenario: Tritone sub keeps dominant function
- **WHEN** `G7` (dominant) is replaced by its tritone sub `Db7`
- **THEN** the replacement is still a dominant-functioning chord resolving to the same target
