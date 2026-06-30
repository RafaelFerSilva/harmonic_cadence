## MODIFIED Requirements

### Requirement: Tonal center is established by Chediak's functional criterion, read from the music

The harness SHALL establish a piece's tonal center by Chediak's **functional-dominant criterion**
(Vol. I pp.84/87): a real-tritone dominant (a `Category.DOMINANT` V7 or SubV7) resolving by bass
to a **repose chord** in a structural/final position makes that chord the tonic. A **repose
chord** SHALL be precise: it MUST NOT itself be a real-tritone dominant (`Category` other than
`DOMINANT`), because the tonic reposes while the dominant is tension (Vol. I pp.84-85) — a V
resolving to another dominant is a secondary-dominant chain link (V/V→V), not a tonic arrival;
and its root MUST equal its bass, because the tonic reposes on its own root — an inverted chord
(e.g. `Fm/C`) is a non-tonic function, not the center. This SHALL be computed **from the chord
symbols alone**, with NO source key annotation as input. The function SHALL return the
Chediak-functional center (its pitch class and major/minor quality, taken from the resolved
repose chord) or `None` when no such functional resolution to a repose chord exists. The Cifra
Club `key` annotation SHALL NOT be consulted.

#### Scenario: The center is found from a functional-dominant resolution to a repose chord
- **WHEN** a progression contains a real-tritone V7/SubV7 resolving by bass to a repose chord (non-dominant, root == bass) in a structural/final position
- **THEN** the harness returns that repose chord's pitch class and quality as the Chediak-functional center
- **AND** it does so without reading any source key annotation

#### Scenario: A dominant-quality target does not establish a tonic
- **WHEN** a real-tritone dominant resolves by bass to a chord that is itself a real-tritone dominant (e.g. `A7(b9)→D7(13)`)
- **THEN** that target does NOT establish the tonic (it is a secondary-dominant chain link, not a repose)
- **AND** the criterion continues searching, returning `None` if no repose target anchors a structural extreme

#### Scenario: An inverted target does not establish a tonic
- **WHEN** a dominant resolves by bass to an inverted chord whose root differs from its bass (e.g. `G7(#5)→Fm/C`)
- **THEN** that target does NOT establish the tonic (the tonic reposes on its own root)
- **AND** the mode is never taken from a chord whose root differs from the candidate bass

#### Scenario: No functional resolution yields no center
- **WHEN** a progression has no real-tritone dominant resolving to a structural repose chord (e.g. a static modal vamp, or only resolutions to dominant/inverted targets)
- **THEN** the Chediak-functional center is `None`
- **AND** the song is quarantined from the center metric (its coverage is reported separately)

#### Scenario: The center is transposition-invariant
- **WHEN** the same piece is presented in two different transpositions
- **THEN** the Chediak-functional center maps by the same interval (the functional relationship is preserved)
- **AND** the agreement verdict against `detect_key` is unchanged
