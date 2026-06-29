## ADDED Requirements

### Requirement: Each curated modal-center fact is admitted through a documented live-verification protocol

A new modal-center fact SHALL be committed to the curated corpus only after passing a
documented admission protocol, so the corpus grows without eroding trust or the inviolable
tonal baseline. For each candidate `(artist, song)`:

1. **Identity resolves** — the candidate's `slug(artist)|slug(song)` MUST resolve to chords
   from the in-process provider; a candidate whose page 404s or whose identity does not
   slug-match what is scraped SHALL be deferred, never guessed.
2. **Center divergence confirmed** — `detect_key` over the scraped chords fixes the
   arrangement's tonal axis; the candidate qualifies ONLY when Chediak's finalis genuinely
   differs from that detected tonal center (`finalis_from_tonal != 0`). A mode-name-only
   divergence (center already correct) SHALL be rejected from this corpus — it belongs to
   part (A) (`modal-mode-naming`).
3. **`finalis_from_tonal` is curated, not subtracted** — the interval SHALL be read from
   Chediak's functional analysis applied to the scraped chords (anchored to the detected
   tonal center), and MUST NOT be computed as `chediak_center_pc − cifra_club_key_pc`
   (absolute cross-source subtraction is invalid when Chediak's edition and the arrangement
   are in different transpositions).
4. **Citation is mandatory** — the fact MUST carry a valid `Citation` (source, volume, page)
   pointing at the specific Chediak page; an uncited or malformed fact fails at import.
5. **Zero tonal regression proven** — after adding the fact, the baseline SHALL be re-run and
   the four Cifra-Club metrics and the tonal `center_accuracy` MUST be identical to before
   (the fact adds only a display annotation and a ledger row).

The corpus invariants (mandatory citation, `finalis_from_tonal` in range and non-zero) SHALL
hold over every committed fact, enforced by the parametrized corpus test.

#### Scenario: A genuine center-divergence candidate is admitted
- **WHEN** a candidate's chords are scraped, `detect_key` fixes the tonal axis, Chediak's finalis differs from it (`finalis_from_tonal != 0`), the page is cited, and the post-add baseline is unchanged
- **THEN** the fact is committed to the curated corpus
- **AND** its curator note and ledger row appear automatically, with the four Cifra-Club metrics and the tonal `center_accuracy` unchanged

#### Scenario: A mode-name-only candidate is rejected from this corpus
- **WHEN** a candidate's detected tonal center already coincides with Chediak's center and only the mode name diverges (`finalis_from_tonal == 0`)
- **THEN** it is NOT admitted to the curated corpus (it is part (A)'s concern)

#### Scenario: An unresolved candidate is deferred, never guessed
- **WHEN** a candidate's page 404s, or its identity does not slug-match the scraped song
- **THEN** the fact is deferred rather than committed with an assumed interval or page
- **AND** the corpus coverage count reflects only committed facts (never overstated)

#### Scenario: The interval is curated from Chediak's reading, not absolute subtraction
- **WHEN** Chediak's edition and the Cifra Club arrangement are in different transpositions
- **THEN** `finalis_from_tonal` is the curated interval relative to the detected tonal center
- **AND** it is never `(chediak_center_pc − cifra_club_key_pc) % 12`
