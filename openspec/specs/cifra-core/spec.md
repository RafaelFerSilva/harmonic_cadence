# cifra-core Specification

## Purpose

The shared `cifra-core` package provides the canonical, single-source-of-truth building blocks consumed by both the scraper and the analyzer: encoding correction, cifra line preprocessing, chord detection, typed song/listing models, and slug normalization. It MUST NOT depend on the scraper or analyzer packages.
## Requirements
### Requirement: Single source of truth for encoding correction

The shared `cifra-core` package SHALL provide one `fix_encoding` implementation, and both the scraper and the analyzer MUST consume it rather than defining their own copies.

#### Scenario: Both packages import the same function
- **WHEN** the scraper or the analyzer corrects mojibake in a cifra line
- **THEN** it calls `cifra_core`'s `fix_encoding`
- **AND** no duplicate `fix_encoding` definition exists in either package

#### Scenario: Mojibake is repaired
- **WHEN** `fix_encoding` receives latin1-misdecoded UTF-8 text (e.g. `"jÃ¡ nÃ£o"`)
- **THEN** it returns the corrected text (`"já não"`)

#### Scenario: Already-correct text is preserved
- **WHEN** `fix_encoding` receives text that is already valid UTF-8 with no mojibake
- **THEN** it returns the text unchanged

#### Scenario: Undecodable input is returned untouched
- **WHEN** `fix_encoding` receives a string that cannot be re-decoded by the correction step
- **THEN** it returns the original input rather than raising

### Requirement: Single source of truth for cifra line preprocessing

The `cifra-core` package SHALL own cifra line cleaning/filtering (tablature, section/structural markers, tuning/instrument lines, blank and consecutive-duplicate lines), exposing one canonical filter consumed by both packages. Line filtering MUST happen in exactly one place in the end-to-end pipeline, and MUST preserve the relative order of the lines it keeps.

#### Scenario: Filtering is not duplicated end-to-end
- **WHEN** a cifra travels from scrape to analysis
- **THEN** tablature/section filtering is applied once according to the documented contract
- **AND** the analyzer does not re-run a second, divergent filter over already-filtered lines

#### Scenario: Filtering is idempotent
- **WHEN** the canonical filter is applied to already-filtered lines
- **THEN** the output equals the input (no further lines are removed or altered)

#### Scenario: Tablature lines are removed
- **WHEN** the input contains guitar-tab lines (e.g. `E|---0---2---`, `B|--1--1--`)
- **THEN** those lines are absent from the output

#### Scenario: Section and structural markers are removed
- **WHEN** the input contains markers such as `[Intro]`, `Parte 1 de 2`, or `tom: C`
- **THEN** those lines are absent from the output

#### Scenario: Instrument tuning lines are removed
- **WHEN** the input contains a tuning line (e.g. `"Afinação Drop D: D A D G B E"`, `"Capotraste na 2ª casa"`)
- **THEN** that line is absent from the output
- **AND** the single-letter note names within it are NOT extracted as chord symbols

#### Scenario: Chord and lyric content is kept in order
- **WHEN** the input mixes chord lines and lyric lines with tablature between them
- **THEN** the chord and lyric lines are retained in their original relative order

#### Scenario: Consecutive duplicate lines are collapsed
- **WHEN** the input contains the same line repeated on adjacent rows
- **THEN** only a single occurrence is kept

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

### Requirement: Typed Cifra and SongRef models

The `cifra-core` package SHALL provide the `Cifra` song model and the `SongRef` listing model used across packages, so the song contract and artist listings have a single typed definition rather than loose dictionaries. The `Cifra` model SHALL carry the song's key (`key`) when the source provides it, distinct from any key detected later by analysis.

#### Scenario: Song contract is typed
- **WHEN** the scraper returns a song and the analyzer reads it
- **THEN** both sides use the `cifra-core` `Cifra` model with fields `artist`, `name`, `cifra`, `cifra_html`, `youtube_url`, `cifraclub_url`, and `key`
- **AND** neither side relies on untyped dictionary access for these fields

#### Scenario: Cifra round-trips through serialization
- **WHEN** a `Cifra` is serialized with `to_dict` and reconstructed with `from_api`
- **THEN** the reconstructed model equals the original, including its `key`

#### Scenario: Key is empty when the source omits it
- **WHEN** a song is built without a source key
- **THEN** the `Cifra` `key` is the empty string

#### Scenario: is_empty reflects absence of chart lines
- **WHEN** a `Cifra` has no chart lines (lyrics-only or instrumental)
- **THEN** `is_empty` is `True`
- **AND** it is `False` when at least one chart line is present

#### Scenario: Cifra is immutable
- **WHEN** code attempts to reassign a field on an existing `Cifra` instance
- **THEN** the attempt raises rather than mutating the model

#### Scenario: SongRef carries listing metadata
- **WHEN** an artist song-list is produced
- **THEN** each entry is a `SongRef` with `name`, `slug`, `url`, and `only_lyrics`

### Requirement: Single slug normalization

The `cifra-core` package SHALL provide one `slugify` function for converting artist and song names into URL/cache slugs, replacing the analyzer's `cifra_slug` and the scraper's inline URL construction. The function MUST be deterministic.

#### Scenario: Accents are stripped and words hyphenated
- **WHEN** `slugify("João Gilberto")` is called
- **THEN** it returns `"joao-gilberto"`

#### Scenario: Case and special characters are normalized
- **WHEN** `slugify` receives mixed-case input with punctuation (e.g. `"Garota de Ipanema!"`)
- **THEN** the result is lowercased, has punctuation removed, and joins words with single hyphens

#### Scenario: Slugify is deterministic
- **WHEN** `slugify` is called twice with the same input
- **THEN** it returns the same result both times

#### Scenario: One definition replaces the duplicates
- **WHEN** the codebase is inspected
- **THEN** slug generation exists only in `cifra_core.slugify`
- **AND** neither package retains its own `cifra_slug` or inline slug-building copy

