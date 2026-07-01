# chord-line-classification Specification

## Purpose

Restrict chord extraction to lines that actually carry chords by classifying each
preserved line as CHORD, LYRIC, or SECTION, and by optionally confirming ambiguous
single-letter tokens against a per-source chord vocabulary. This removes phantom
single-letter chords harvested from capitalized prose without mutating the line stream
or regressing the functional baseline.
## Requirements
### Requirement: Line classification by chord density

The `cifra-core` package SHALL provide one canonical line classifier that labels each
preserved line as CHORD, LYRIC, or SECTION, so that chord extraction can be restricted to
CHORD lines. A line SHALL be classified CHORD when the ratio of **chord-position tokens** to total
whitespace-separated tokens meets or exceeds a configured threshold (default ≈ 0.6); a line
that is mostly prose SHALL be classified LYRIC; a structural marker SHALL be classified
SECTION. A **chord-position token** is a token that is either a valid chord (`is_chord_token`) or a
**malformed chord** (`malformed_chord_token`) — the latter counted so that a line dominated by
malformed-but-clearly-chord tokens (e.g. `D9/S / E/D / D9/S`, an invalid `/S` bass) is not
misclassified LYRIC and its valid chords silently dropped. Classification SHALL be a pure read over
the line text — it MUST NOT remove, reorder, or mutate lines, and MUST NOT change
`clean_cifra_lines` output.

#### Scenario: A chord line is classified CHORD
- **WHEN** the classifier receives a line like `C / / G / Am` or `Bm7      E7(b9)    Am7 /`
- **THEN** it returns CHORD (high ratio of valid-chord tokens)

#### Scenario: A line dominated by malformed chords is still CHORD
- **WHEN** the classifier receives a line like `D9/S / E/D / D9/S` (an invalid `/S` bass on a chord vamp)
- **THEN** it returns CHORD (malformed chords count as chord-position tokens)
- **AND** the valid chords on that line (e.g. `E/D`) are not silently dropped

#### Scenario: A lyric line is classified LYRIC
- **WHEN** the classifier receives a prose line like `Com seu passado E tradição` or `É livre e é feliz E tem tudo o que quis`
- **THEN** it returns LYRIC (most tokens are not chord-position tokens)
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

### Requirement: Malformed chord notations are detected and reported, not silently dropped

The `cifra-core` package SHALL provide `malformed_chord_token`, which identifies a token that is a
**malformed chord** — clearly intended as a chord but not fully parseable. A token is malformed
when ALL of: (a) it is not a complete valid chord (`is_chord_token` is false); (b) it has a
non-empty **valid chord prefix** (the canonical chord regex matches at its start); (c) the
remainder immediately after that prefix **starts with `/` or `(`** (a bass or tension attempt),
which scopes detection to chord positions and spares lyric words; and (d) after removing ALL valid
chord substrings and the decoration characters (`/`, `|`, `%`, `-`, whitespace), **garbage
residue** remains, which spares valid chords glued by bar-separators.

Chord extraction SHALL collect malformed tokens (via an optional `unidentified` output) and SHALL
NOT extract a guessed chord from them (it MUST NOT emit the valid prefix `D9` from `D9/S`). All
other tokens SHALL continue through the existing extraction (bar-separators, valid inverted basses,
and space-less glued chords remain intact). When no `unidentified` collector is supplied, malformed
tokens are simply not extracted (never guessed).

#### Scenario: A malformed chord is reported and not guessed
- **WHEN** extraction reads the token `D9/S` (valid prefix `D9`, invalid `/S` bass) on a CHORD line
- **THEN** `D9/S` is collected as an unidentified notation
- **AND** no chord (in particular not the guessed `D9`) is extracted from it

#### Scenario: A chord with a trailing bar-separator is not malformed
- **WHEN** the token is `Am7/`, `A7(b9)/`, `Bb7(9)///`, or `B°/A/` (a valid chord followed only by bar-separators)
- **THEN** it is NOT malformed and the valid chord (`Am7`, `A7(b9)`, `Bb7(9)`, `B°/A`) is extracted

#### Scenario: Chords glued by bar-separators are not malformed
- **WHEN** the token is `Gm7(11)///Gb7(#11)///` (two valid chords joined by bar-separators, no spaces)
- **THEN** it is NOT malformed (the residue is empty) and both chords are extracted

#### Scenario: A lyric word is not a malformed chord
- **WHEN** the token is `Brasil` (a valid root prefix `B` but the remainder does not start with `/` or `(`)
- **THEN** it is NOT malformed (it is out of scope; the existing bare-root whitelist governs it)

