## MODIFIED Requirements

### Requirement: Line classification by chord density

The `cifra-core` package SHALL provide one canonical line classifier that labels each
preserved line as CHORD, LYRIC, or SECTION, so that chord extraction can be restricted to
CHORD lines. A line SHALL be classified CHORD when the ratio of **chord-position tokens** to total
whitespace-separated tokens meets or exceeds a configured threshold (default ≈ 0.6); a line
that is mostly prose SHALL be classified LYRIC; a structural marker SHALL be classified
SECTION. A **chord-position token** is a token that is either a valid chord (`is_chord_token`), a
**malformed chord** (`malformed_chord_token`), or a **glued chord token** — a token that is
entirely composed of one or more valid chords plus decoration characters, with **empty residue**
after removing all valid chord substrings and decoration (e.g. `Am6/`, `Bb7(9)///`, `B°/A/`,
`Gm7(11)///Gb7(#11)///`). The glued-chord criterion SHALL be the same empty-residue test already
used by clause (d) of `malformed_chord_token` (inverted), so that classification and extraction
agree on what counts as a chord position: any token the extractor would rescue via `find_all`
SHALL also count toward density. A token composed **only** of decoration characters (`/`, `|`,
`%`, `-`, `—`, `·`, in any run length) SHALL NOT count in the density denominator.
Classification SHALL be a pure read over the line text — it MUST NOT remove, reorder, or mutate
lines, and MUST NOT change `clean_cifra_lines` output.

#### Scenario: A chord line is classified CHORD

- **WHEN** the classifier receives a line like `C / / G / Am` or `Bm7      E7(b9)    Am7 /`
- **THEN** it returns CHORD (high ratio of valid-chord tokens)

#### Scenario: A line dominated by glued chord tokens is CHORD

- **WHEN** the classifier receives a line like `C#m7 /  Am6/  C#m7 /  F#7 /  Bm7/ / /  Gm6/ / /`
  (valid chords glued to rhythm-bar separators)
- **THEN** it returns CHORD (glued chord tokens count as chord-position tokens)
- **AND** the extractor harvests every chord on the line (`C#m7`, `Am6`, `F#7`, `Bm7`, `Gm6`),
  none silently dropped

#### Scenario: A line dominated by malformed chords is still CHORD

- **WHEN** the classifier receives a line like `D9/S / E/D / D9/S` (an invalid `/S` bass on a chord vamp)
- **THEN** it returns CHORD (malformed chords count as chord-position tokens)
- **AND** the valid chords on that line (e.g. `E/D`) are not silently dropped

#### Scenario: A lyric line is classified LYRIC

- **WHEN** the classifier receives a prose line like `Com seu passado E tradição` or `É livre e é feliz E tem tudo o que quis`
- **THEN** it returns LYRIC (most tokens are not chord-position tokens)
- **AND** no chord token is harvested from that line by the chord extractor

#### Scenario: A lyric word with a chord-letter prefix is not a chord-position token

- **WHEN** a token like `Dado/` or `Brasil` appears (chord-letter prefix but non-empty residue)
- **THEN** it does not count as a chord-position token (the residue after removing valid chords
  and decoration is non-empty)

#### Scenario: Pure-decoration runs do not dilute density

- **WHEN** the classifier receives a line containing tokens like `///` or `|—|` between chords
- **THEN** those tokens do not count in the density denominator

#### Scenario: A structural marker is classified SECTION

- **WHEN** the classifier receives a line like `Introdução:` or a residual section marker
- **THEN** it returns SECTION

#### Scenario: Classification does not mutate the line stream

- **WHEN** the classifier runs over the lines kept by `clean_cifra_lines`
- **THEN** the lines themselves are unchanged in content and order
- **AND** `clean_cifra_lines` remains idempotent and continues to preserve lyric lines for display
