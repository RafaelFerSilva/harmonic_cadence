## ADDED Requirements

### Requirement: Line classification by chord density

The `cifra-core` package SHALL provide one canonical line classifier that labels each
preserved line as CHORD, LYRIC, or SECTION, so that chord extraction can be restricted to
CHORD lines. A line SHALL be classified CHORD when the ratio of valid-chord tokens to total
whitespace-separated tokens meets or exceeds a configured threshold (default ≈ 0.6); a line
that is mostly prose SHALL be classified LYRIC; a structural marker SHALL be classified
SECTION. Classification SHALL be a pure read over the line text — it MUST NOT remove,
reorder, or mutate lines, and MUST NOT change `clean_cifra_lines` output.

#### Scenario: A chord line is classified CHORD
- **WHEN** the classifier receives a line like `C / / G / Am` or `Bm7      E7(b9)    Am7 /`
- **THEN** it returns CHORD (high ratio of valid-chord tokens)

#### Scenario: A lyric line is classified LYRIC
- **WHEN** the classifier receives a prose line like `Com seu passado E tradição` or `É livre e é feliz E tem tudo o que quis`
- **THEN** it returns LYRIC (most tokens are not valid chords)
- **AND** no chord token is harvested from that line by the chord extractor

#### Scenario: A structural marker is classified SECTION
- **WHEN** the classifier receives a line like `Introdução:` or a residual section marker
- **THEN** it returns SECTION

#### Scenario: Classification does not mutate the line stream
- **WHEN** the classifier runs over the lines kept by `clean_cifra_lines`
- **THEN** the lines themselves are unchanged in content and order
- **AND** `clean_cifra_lines` remains idempotent and continues to preserve lyric lines for display

### Requirement: Optional chord-vocabulary whitelist confirms ambiguous tokens

Chord extraction SHALL accept an OPTIONAL set of known chord symbols (a per-source
vocabulary whitelist). When a whitelist is supplied, an ambiguous single-letter token (a
bare `A–G` root with no quality and no bass) SHALL be admitted as a chord only if it appears
in the whitelist; otherwise it SHALL be rejected. When no whitelist is supplied, extraction
SHALL fall back to line classification alone (the bare token is admitted only from a line
classified CHORD). The whitelist SHALL be derivable from a source-provided chord vocabulary
(e.g. the `Acordes Utilizados:` header of a corpus `.md`).

#### Scenario: Ambiguous bare token rejected when absent from the whitelist
- **WHEN** extraction runs with a whitelist that does NOT contain the bare symbol `B`
- **AND** the candidate `B` arises from a lyric word like `Brasil`
- **THEN** `B` is not extracted as a chord

#### Scenario: Ambiguous bare token admitted when present in the whitelist
- **WHEN** extraction runs with a whitelist that contains the bare symbol `A`
- **AND** a CHORD line legitimately contains the standalone triad `A`
- **THEN** `A` is extracted as a chord

#### Scenario: Whitelist is optional
- **WHEN** extraction runs without any whitelist
- **THEN** ambiguous bare tokens are admitted only from lines classified CHORD
- **AND** extraction still succeeds (the classifier alone resolves the majority of phantoms)

### Requirement: Chord extraction reads only chord lines

The chord-extraction step that feeds the analysis engine SHALL harvest chord symbols only
from lines classified CHORD, applying the optional whitelist to ambiguous tokens. Lines
classified LYRIC or SECTION SHALL contribute no chord tokens. This SHALL be the single
extraction path; no parallel extractor that scans every line MAY remain.

#### Scenario: Lyric lines contribute no chords end to end
- **WHEN** a cifra mixing chord lines and lyric lines is analyzed
- **THEN** the engine's chord sequence contains only tokens harvested from CHORD lines
- **AND** the count of single-letter phantom tokens from prose drops to ≈ 0

#### Scenario: The functional baseline does not regress
- **WHEN** `scripts/songbook_baseline.py` runs over the local corpus after this change
- **THEN** the functional invariant (real tritone ⇒ dominant) remains 62/62
- **AND** the last extracted chord of the previously-affected songs is no longer a lyric word
