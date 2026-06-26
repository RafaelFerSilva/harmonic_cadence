## MODIFIED Requirements

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
