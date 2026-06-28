## ADDED Requirements

### Requirement: Degree-relative modal center accuracy over the Chediak provenance tier

The harness SHALL report a **modal center accuracy** metric (`modal_center_accuracy`)
that scores how often the detected modal center (the finalis from the modal-center
arbitration overlay) matches the structurally correct modal center, over the
`chediak`-provenance subset of the structural gold (the modal facts already committed —
e.g. Arrastão = A dorian, p.125). This activates the `chediak` tier that the tonal
center metric deferred.

The metric SHALL be computed **degree-relative**, in the single `(detected − cifra_club_key) % 12`
frame: a detection is correct when `(detected_center_pc − cifra_club_key_pc) % 12 ==
structural_offset`. The `structural_offset` for a modal entry SHALL be a **curated degree
fact** — the finalis's scale degree relative to the Cifra Club key, taken from Chediak's
functional reading of the piece — and MUST NOT be derived by absolute cross-source pitch
subtraction (`chediak_center_pc − cifra_club_key_pc`), because Chediak's analysis and the
Cifra Club arrangement may be in different transpositions (e.g. "Pra não dizer…" Chediak E
vs Cifra Club F). Both operands of the comparison (`detected_center_pc` and
`cifra_club_key_pc`) come from the Cifra Club arrangement, so the metric is invariant to
any transposition of that arrangement.

`modal_center_accuracy` SHALL be additive: the four Cifra-Club metrics (mode, exact,
relative-aware, collection) and the tonal `center_accuracy` (over the `verified` tier)
SHALL be unchanged. The metric SHALL be reported over the `chediak`-tier subset only, with
that subset's size reported alongside so coverage is visible.

#### Scenario: A correct modal center counts toward modal center accuracy
- **WHEN** a `chediak`-tier song's detected modal center matches its curated degree offset (e.g. Arrastão: detected finalis Lá, Cifra Club key Ré, offset +7)
- **THEN** the song counts toward `modal_center_accuracy`
- **AND** the four Cifra-Club metrics and the tonal `center_accuracy` are computed exactly as before

#### Scenario: The modal offset is a curated degree fact, not absolute subtraction
- **WHEN** Chediak's analysis and the Cifra Club arrangement are in different transpositions (e.g. Chediak E aeolian, Cifra Club F minor)
- **THEN** the gold `structural_offset` is the finalis's curated scale degree relative to the Cifra Club key, not `(chediak_center_pc − cifra_club_key_pc) % 12`
- **AND** a correct detection in the Cifra Club arrangement is not penalised by the transposition gap

#### Scenario: Modal center accuracy is invariant to transposition
- **WHEN** a `chediak`-tier song's chords and its Cifra Club key are both transposed by the same interval
- **THEN** the `modal_center_accuracy` verdict for that song is unchanged
- **AND** this holds because the metric compares the detected-to-key offset, not absolute pitch

#### Scenario: A wrong-center detection counts as a modal miss
- **WHEN** a `chediak`-tier song's detected center does not match its curated degree offset (e.g. the tonal axis is detected instead of the modal finalis)
- **THEN** the song does NOT count toward `modal_center_accuracy`
- **AND** it is listed in the per-song modal center hole

### Requirement: Baseline reports modal center accuracy live against the corpus

When `scripts/key_baseline.py` runs, its output SHALL include a `modal_center_accuracy`
line over the `chediak`-tier subset, alongside the existing four Cifra-Club metrics and
the tonal center-accuracy line, and SHALL list the per-song **modal center hole** (the
modal songs whose detected center does not match the curated offset). Adding this line
SHALL NOT change the four Cifra-Club metric values nor the tonal center-accuracy value.

#### Scenario: Aggregate output includes the modal center line
- **WHEN** the baseline runs
- **THEN** the aggregate metrics include a `modal_center_accuracy` line over the `chediak`-tier subset, with that subset's size shown
- **AND** the four Cifra-Club metric values and the tonal center-accuracy value are unchanged by this addition

#### Scenario: The modal center hole is listed per song
- **WHEN** a `chediak`-tier song's detected modal center does not match its curated offset
- **THEN** the per-song output lists it with its Cifra Club key, curated offset, and detected center all visible

## MODIFIED Requirements

### Requirement: Structural center gold and transposition-invariant center accuracy

The harness SHALL support a second, structural gold — the **tonal center per Chediak**
(the theoretical arbiter) — alongside the Cifra Club key gold, and SHALL report a
**center accuracy** metric that counts a detection as correct when its detected tonal
center matches the structural center, independent of absolute transposition.

Center accuracy SHALL be computed by offset, not absolute pitch:
`(detected_tonic_pc - cifra_club_key_pc) % 12 == structural_offset`, where
`structural_offset` is the semitone offset from the Cifra Club key to the structurally
correct center (`0` when the Cifra Club key already names the true center). Because the
Cifra Club key and the detection share the scraped arrangement's pitch space, the metric
is invariant to any transposition of that arrangement. The metric judges the **center
pitch**, not the major/minor label (mode is covered by mode accuracy).

The **tonal** center metric covers `structural_offset = 0` (the Cifra Club key confirmed as
the true tonic) over the `verified` tier. **Modal** centers, where the structural center
diverges from the Cifra Club key (non-zero offset, e.g. Arrastão = A dorian), are scored by
the separate `modal_center_accuracy` metric over the `chediak` tier (see "Degree-relative
modal center accuracy"); their offset is a curated degree fact, NOT absolute pitch
subtraction, because Chediak's analysis and the Cifra Club arrangement may be in different
transpositions. The two metrics are reported separately and are mutually additive.

The structural gold SHALL be a committed list of **facts** — `(song, cifra_club_key,
structural_offset, center_type, mode, provenance, justification)` — never the book's
harmonizations, chord tables, or chord sheets. Each entry SHALL carry a **provenance**
tier, because the Cifra Club key is a transposition anchor, NOT an authoritative source of
the tonal center:

- `verified` — the center is independently confirmed by a documented mechanical criterion
  (a functional dominant — a true V7 tritone — resolving to the Cifra Club key as a
  structural/final cadence), with the criterion recorded in the justification. This is the
  tier the **tonal** center metric runs over (`structural_offset = 0`).
- `chediak` — the center is taken from the book with a cited page (e.g. Arrastão = A
  dorian, p.125). This is the tier the **modal** center metric (`modal_center_accuracy`)
  runs over; its `structural_offset` is a curated degree fact.
- `unverified` — neither holds; the song is quarantined and excluded from both center
  metrics.

`structural_offset = 0` SHALL be a verified claim (provenance `verified`), NOT a default
inherited from the Cifra Club annotation. Tonal center accuracy SHALL be reported over the
`verified` subset only; modal center accuracy over the `chediak` subset only; the
`unverified` count SHALL be reported separately so coverage is visible. Both center metrics
are additive: the existing mode, exact, relative-aware, and collection metrics are
unchanged.

#### Scenario: Center accuracy counts a wrong-degree detection as a miss
- **WHEN** the tonic is verified (offset 0) and the detection centers on another diatonic degree (e.g. the dominant V or the mediant iii) instead
- **THEN** the song does NOT count toward tonal center accuracy
- **AND** the Cifra Club exact/relative/collection metrics are computed exactly as before

#### Scenario: Modal centers are scored by the modal center metric
- **WHEN** a song's structural center diverges from the Cifra Club key (a modal final, non-zero offset)
- **THEN** it is NOT scored by the tonal center accuracy (the `verified` tier)
- **AND** its Chediak center fact (provenance `chediak`, curated degree offset) is scored by `modal_center_accuracy`

#### Scenario: Center accuracy is invariant to transposition
- **WHEN** a song's chords and its Cifra Club key are both transposed by the same interval
- **THEN** the center-accuracy verdict for that song is unchanged
- **AND** this holds because the metric compares the detected-to-key offset, not absolute pitch

#### Scenario: Unverified songs are quarantined from center accuracy
- **WHEN** a song has neither a Chediak citation nor an independently verified functional-dominant resolution to its Cifra Club key
- **THEN** it is marked `unverified` and excluded from both center-accuracy denominators
- **AND** its count is reported separately so coverage is visible
- **AND** `structural_offset = 0` is never assumed for it by default

#### Scenario: Structural gold stores only facts, never the book's harmonizations
- **WHEN** the structural gold is committed to the repository
- **THEN** it contains only `(song, key, offset, center_type, mode, page)` facts
- **AND** no chord sheet, harmonization, or analysis table from the book is stored; chords are re-fetched from Cifra Club
