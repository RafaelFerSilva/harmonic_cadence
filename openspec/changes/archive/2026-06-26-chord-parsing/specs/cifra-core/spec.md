## MODIFIED Requirements

### Requirement: Canonical chord-detection pattern

The `cifra-core` package SHALL provide the one chord-detection regex used across packages for recognizing and extracting chord symbols. It MUST capture the full symbol — root, quality, parenthesized tensions in both the `#`/`b` and the `+`/`-` dialect, power chords, and a slash bass — and MUST distinguish a slash followed by a note (an inverted bass) from a slash followed by a digit (an added-tone group).

#### Scenario: Chord detection has one definition
- **WHEN** any package needs to detect or extract chord symbols from a line
- **THEN** it uses the chord pattern provided by `cifra-core`
- **AND** no package defines its own separate chord regex

#### Scenario: Simple and complex chords are matched
- **WHEN** a line contains chords such as `C`, `Am7`, `G/B`, `F#m7b5`, `Bb7(9)`, `E7M(9)`
- **THEN** each chord symbol is extracted in full, including bass note and parenthesized extensions

#### Scenario: Cifra Club ± alterations are captured in full
- **WHEN** a line contains chords such as `A7(13-)`, `Db7(5+/9+)`, `Em7(5-)`, `D7(9/11+)`
- **THEN** each chord symbol is extracted in full, including the parenthesized altered tones

#### Scenario: Power chords are not truncated
- **WHEN** a line contains `C5` or `G5`
- **THEN** the symbol is extracted as `C5` / `G5` (not truncated to `C` / `G`)

#### Scenario: Slash digit is an added tone, slash note is a bass
- **WHEN** a line contains `C6/9`
- **THEN** the whole symbol `C6/9` is extracted (the `/9` is an added-tone group, not a bass)
- **AND** when a line contains `C/Bb`, the symbol is extracted with `Bb` as the bass

#### Scenario: Plain words are not matched as chords
- **WHEN** a line contains lyric words that are not chords
- **THEN** no chord symbol is extracted from those words
