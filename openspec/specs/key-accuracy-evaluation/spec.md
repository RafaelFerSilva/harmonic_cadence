# key-accuracy-evaluation Specification

## Purpose
TBD - created by archiving change validation-harness. Update Purpose after archive.
## Requirements
### Requirement: Multi-key gold for modulating songs

The harness SHALL support songs annotated with multiple gold keys — a primary tonality and one or more secondary tonalities — so that genuinely modulating pieces (per Chediak's modulação por acorde pivô, p. 118) are evaluated against their full tonal structure rather than a single label.

For a modulating song:
- **Primary acerto** (partial): the detected key matches the primary gold.
- **Full acerto** (total): `dominant_regions` detects all gold keys as dominant regions.
- **Erro**: neither the primary nor any secondary gold key is detected.

Monotonal songs (single gold key) are unaffected — their evaluation logic is unchanged.

#### Scenario: Modulating song with correct primary detection counts as partial acerto
- **WHEN** a modulating song is evaluated and `detect_key` returns the primary gold key
- **THEN** the result is `primary_ok=True`
- **AND** it does NOT count as a full acerto unless all secondary keys are also found in `dominant_regions`

#### Scenario: Modulating song with all regions detected counts as full acerto
- **WHEN** `dominant_regions` for a modulating song contains regions matching both the primary and all secondary gold keys
- **THEN** the result is `all_ok=True` and `primary_ok=True`

#### Scenario: Monotonal evaluation is unchanged
- **WHEN** a song with a single gold key is evaluated
- **THEN** it uses the existing `KeyEval` logic (exact / relative / erro)
- **AND** no new fields are added to its evaluation record

#### Scenario: Modulating songs are reported separately in the baseline
- **WHEN** `key_baseline.py` runs
- **THEN** modulating songs appear in a separate section of the output with primary/full acerto indicated
- **AND** they are excluded from the aggregate monotonal metrics (mode %, exact %, relative-aware %) to avoid distorting the baseline

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

