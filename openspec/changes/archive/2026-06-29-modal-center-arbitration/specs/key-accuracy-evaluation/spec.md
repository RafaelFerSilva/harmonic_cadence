## ADDED Requirements

### Requirement: Modal center is reported as a coverage + divergence ledger, not a detection accuracy

The harness SHALL report the curated modal centers as a **coverage count** plus a **divergence ledger** — NOT an accuracy metric — because nothing is detected (the modal center is a cited fact, so an "accuracy" would trivially assert its own gold). Over the curated set, the ledger SHALL list, per song, `(detected tonal center, curated modal center + mode, finalis_from_tonal interval, page)`, quantifying the gap between the arrangement's tonal axis and Chediak's conception. The coverage count SHALL report how many curated songs carry a detected tonal axis so coverage is never overstated. This addition SHALL leave the four Cifra-Club metrics (mode, exact, relative-aware, collection) and the tonal `center_accuracy` (over the `verified` tier) byte-identical.

The ledger SHALL be **transposition-safe**: each row carries the **curated** `finalis_from_tonal` interval (the finalis relative to the detected tonal center, read from Chediak's analysis onto the scraped chords), and the implied finalis pitch SHALL be derived by **adding** that interval to the detected tonal center — never by absolute cross-source subtraction (`chediak_center_pc − cifra_club_key_pc`), which breaks when Chediak's edition and the Cifra Club arrangement are in different transpositions.

#### Scenario: The curated set is reported as coverage + ledger, not accuracy
- **WHEN** the harness reports the curated modal centers (e.g. Arrastão, Procissão)
- **THEN** it emits a coverage count and a per-song divergence ledger `(detected tonal center, curated center + mode, finalis_from_tonal, page)`
- **AND** no modal "accuracy" percentage is produced
- **AND** the four Cifra-Club metrics and the tonal `center_accuracy` are unchanged

#### Scenario: The ledger uses the curated interval, not absolute subtraction
- **WHEN** Chediak's edition and the Cifra Club arrangement are in different transpositions
- **THEN** the ledger row's `finalis_from_tonal` is the curated interval, and the implied finalis is the detected tonal center plus that interval
- **AND** it is never `(chediak_center_pc − cifra_club_key_pc) % 12`

#### Scenario: The ledger is invariant to transposition of the arrangement
- **WHEN** a curated song's chords (and so its detected tonal center) are transposed by some interval
- **THEN** the row's `finalis_from_tonal` is unchanged
- **AND** the implied finalis pitch moves by the same interval, tracking the arrangement

### Requirement: Baseline reports the modal-center coverage + ledger live, without moving any tonal metric

When `scripts/key_baseline.py` runs, its output SHALL include a modal-center coverage + ledger block over the curated set — the detected tonal axis beside Chediak's modal center, the `finalis_from_tonal` interval, and the page — labeled explicitly as a cited fact, NOT a detection. Adding this block SHALL NOT change the four Cifra-Club metric values nor the tonal center-accuracy value.

#### Scenario: Aggregate output includes the modal-center ledger
- **WHEN** the baseline runs
- **THEN** the output includes the curated coverage count and the per-song modal-center ledger
- **AND** the four Cifra-Club metric values and the tonal center-accuracy value are unchanged by this addition

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
diverges from the Cifra Club key (non-zero offset, e.g. Arrastão = A dorian), are NOT
scored by any accuracy — the modal center is unrecoverable from the chords (a cited fact,
not a detection), so they are reported by the separate **coverage + divergence ledger**
over the `chediak` tier (see "Modal center is reported as a coverage + divergence ledger").
Their `finalis_from_tonal` is a curated interval, NOT absolute pitch subtraction, because
Chediak's analysis and the Cifra Club arrangement may be in different transpositions. The
tonal metric and the modal ledger are reported separately and are mutually additive.

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
  dorian, p.125). This is the tier the **modal center coverage + ledger** runs over; its
  `finalis_from_tonal` is a curated interval fact, not a detection.
- `unverified` — neither holds; the song is quarantined and excluded from the tonal center
  metric.

`structural_offset = 0` SHALL be a verified claim (provenance `verified`), NOT a default
inherited from the Cifra Club annotation. Tonal center accuracy SHALL be reported over the
`verified` subset only; the modal centers over the `chediak` subset are reported as a
coverage + ledger; the `unverified` count SHALL be reported separately so coverage is
visible. Both reports are additive: the existing mode, exact, relative-aware, and
collection metrics are unchanged.

#### Scenario: Center accuracy counts a wrong-degree detection as a miss
- **WHEN** the tonic is verified (offset 0) and the detection centers on another diatonic degree (e.g. the dominant V or the mediant iii) instead
- **THEN** the song does NOT count toward tonal center accuracy
- **AND** the Cifra Club exact/relative/collection metrics are computed exactly as before

#### Scenario: Modal centers are reported by the ledger, not the tonal accuracy
- **WHEN** a song's structural center diverges from the Cifra Club key (a modal final, non-zero offset)
- **THEN** it is NOT scored by the tonal center accuracy (the `verified` tier)
- **AND** its Chediak center fact (provenance `chediak`, curated interval) is reported in the modal-center coverage + divergence ledger

#### Scenario: Center accuracy is invariant to transposition
- **WHEN** a song's chords and its Cifra Club key are both transposed by the same interval
- **THEN** the center-accuracy verdict for that song is unchanged
- **AND** this holds because the metric compares the detected-to-key offset, not absolute pitch

#### Scenario: Unverified songs are quarantined from center accuracy
- **WHEN** a song has neither a Chediak citation nor an independently verified functional-dominant resolution to its Cifra Club key
- **THEN** it is marked `unverified` and excluded from the tonal center-accuracy denominator
- **AND** its count is reported separately so coverage is visible
- **AND** `structural_offset = 0` is never assumed for it by default

#### Scenario: Structural gold stores only facts, never the book's harmonizations
- **WHEN** the structural gold is committed to the repository
- **THEN** it contains only `(song, key, offset, center_type, mode, page)` facts
- **AND** no chord sheet, harmonization, or analysis table from the book is stored; chords are re-fetched from Cifra Club
