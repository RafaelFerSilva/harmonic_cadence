# key-accuracy-evaluation Specification

## Purpose
TBD - created by archiving change validation-harness. Update Purpose after archive.
## Requirements
### Requirement: Key-detection accuracy harness

The project SHALL provide a harness that evaluates key-detection accuracy against annotated keys. Given a corpus of `(name, chords, annotated_key)`, it SHALL report four metrics: **mode accuracy** (major/minor), **exact accuracy** (tonic and mode), **relative-aware accuracy** (counting a detection that differs from the annotation only by the relative major/minor as a near-match), and **collection accuracy** (counting a detection whose tonic is a diatonic degree of the annotated key's scale — i.e. the correct diatonic collection / key signature — even when the tonal center within it is wrong). An annotated key is parsed from a label where a trailing `m` denotes minor (e.g. `"G"` = G major, `"Am"` = A minor).

Collection accuracy is computed by `same_collection(gold, detected)`: `True` when `(detected_tonic_pc - gold_tonic_pc) % 12` is a member of the gold's diatonic offset set (major `{0,2,4,5,7,9,11}`, minor natural `{0,2,3,5,7,8,10}`). It ignores the detected major/minor label, because that label is unreliable for modal pieces (e.g. K-S reports "E minor" for an E-Phrygian piece whose collection is C major's).

#### Scenario: An exact detection counts toward all metrics
- **WHEN** the detected key equals the annotated key (same tonic and mode)
- **THEN** the song counts toward mode, exact, relative-aware, and collection accuracy

#### Scenario: A relative-only difference is a near-match
- **WHEN** the annotation is C major and the detection is A minor (its relative)
- **THEN** the song counts toward relative-aware accuracy
- **AND** it does NOT count toward exact accuracy

#### Scenario: A diatonic-degree detection counts toward collection accuracy
- **WHEN** the annotation is C major and the detection centers on a diatonic degree of C major other than the relative (e.g. E minor = the mediant iii, or G = the dominant V)
- **THEN** the song counts toward collection accuracy
- **AND** it does NOT count toward exact accuracy
- **AND** it does NOT count toward relative-aware accuracy (unless it is also the relative)

#### Scenario: A non-diatonic detection fails collection accuracy
- **WHEN** the detected tonic is not a diatonic degree of the annotated key (e.g. annotation A major, detection C major — C is not in the A-major scale)
- **THEN** the song does NOT count toward collection accuracy

#### Scenario: Metrics are nested by permissiveness
- **WHEN** a corpus is evaluated
- **THEN** relative-aware accuracy is greater than or equal to exact accuracy
- **AND** collection accuracy is greater than or equal to relative-aware accuracy

#### Scenario: Only annotated songs are evaluated
- **WHEN** the corpus is loaded from a directory
- **THEN** songs without an annotated key are excluded from the evaluation

#### Scenario: The baseline reports the collection metric per song and in aggregate
- **WHEN** `scripts/key_baseline.py` runs
- **THEN** the aggregate output includes a collection (key-signature) accuracy line alongside mode, exact, and relative-aware
- **AND** a song that matches the collection but not the exact center is shown with a distinct verdict (e.g. "coleção"), reserving the error verdict for a wrong diatonic collection

### Requirement: Real-song baseline uses the source's own key as independent gold

The real-song key-detection baseline SHALL annotate each song with the **source's
own key** (the Cifra Club "tom") as the gold, rather than an external authority.
Because the gold and the chords come from the same source, there is **no
transposition gap**, so exact-tonic accuracy is a meaningful first-class metric for
this baseline (not merely a relative-aware approximation).

The baseline corpus SHALL be a committed list of **facts** — `(artist, song, key)`
— and MUST NOT store the chord sheets themselves; the chords are fetched at run time
and discarded. This keeps the corpus independent and within the project's source
boundary (the book's analyzed-song tables are not ingested as fixtures).

#### Scenario: Gold annotation is the source key, not an external authority

- **WHEN** a song is evaluated in the real-song baseline
- **THEN** its gold key is the key annotated by the chord source (Cifra Club)
- **AND** the detected key is compared against that same-source gold

#### Scenario: Exact-tonic accuracy is meaningful (no transposition confound)

- **WHEN** the baseline reports its metrics
- **THEN** exact-tonic accuracy reflects detection quality directly, because gold and
  chords share one source and are not transposed relative to each other

#### Scenario: Only facts are stored, not chord sheets

- **WHEN** the baseline corpus is committed to the repository
- **THEN** it contains only `(artist, song, key)` facts
- **AND** no chord sheet content is stored; chords are re-fetched at run time

#### Scenario: Corpus is curated against real fetchability

- **WHEN** a candidate song cannot be fetched or carries no source key
- **THEN** it is excluded from the committed corpus
- **AND** the corpus reflects only songs verified to fetch with an annotated key

### Requirement: Baseline documents expected accuracy after each calibration change

After any recalibration of key-detection parameters (weights, band thresholds), the project SHALL run `scripts/key_baseline.py` against the full corpus (n≥60, chords fetched live) and record the resulting metrics — mode, exact, and relative-aware accuracy — in `ROADMAP.md`. A song that previously produced an error result and now produces an exact or relative match MUST be explicitly noted as a resolved case.

#### Scenario: Recalibration is followed by a baseline run

- **WHEN** a key-detection parameter (e.g. `TIE_BAND`) is changed
- **THEN** the baseline script is executed before the change is archived
- **AND** the new metrics are committed to `ROADMAP.md`

#### Scenario: Resolved cases are recorded

- **WHEN** a song transitions from an incorrect detection to a correct one after a parameter change
- **THEN** it is noted in `ROADMAP.md` as a resolved case for that change
- **AND** the previous metric baseline is documented alongside the new one to show the delta

#### Scenario: No regressions are introduced

- **WHEN** the baseline is run after a parameter change
- **THEN** no song that was previously detected correctly transitions to an incorrect detection
- **AND** if a regression is found, the parameter change is rolled back or adjusted before archiving

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

The tonal `center_accuracy` SHALL run over **two** tonal tiers, mutually additive:

- `verified` — `structural_offset = 0`, the Cifra Club key independently confirmed as the
  true tonic by a functional dominant resolving to it (`verify_tonal_center`).
- `chediak`-**tonal** — the tonal center taken from Chediak's Parte 4 "Tom de X maior/menor"
  label with a cited page. Its `structural_offset` is a **curated degree fact**: the role
  Chediak's tonic plays relative to the Cifra Club annotation (the CC label names the tonic
  → `0`; the CC label names the relative minor of Chediak's major tonic → `+3`; the relative
  major of Chediak's minor tonic → `-3`; another degree → that degree's offset). It MUST NOT
  be derived by absolute cross-source subtraction (`chediak_tom_pc − cifra_club_key_pc`),
  because Chediak's edition and the Cifra Club arrangement may be in different transpositions.

**Modal** centers, where the structural center diverges from the Cifra Club key (a modal
final, `center_type = modal`), are NOT scored by any accuracy — the modal center is
unrecoverable from the chords (a cited fact, not a detection), so they are reported by the
separate **coverage + divergence ledger** over the `chediak` tier (see "Modal center is
reported as a coverage + divergence ledger"). The `chediak` provenance tier therefore
carries BOTH tonal facts (→ `center_accuracy`) and modal facts (→ the ledger), routed by
`center_type`. The tonal metric and the modal ledger are reported separately and are
mutually additive.

The structural gold SHALL be a committed list of **facts** — `(song, cifra_club_key,
structural_offset, center_type, mode, provenance, justification)` — never the book's
harmonizations, chord tables, or chord sheets. Each entry SHALL carry a **provenance**
tier, because the Cifra Club key is a transposition anchor, NOT an authoritative source of
the tonal center:

- `verified` — the center is independently confirmed by a documented mechanical criterion
  (a functional dominant — a true V7 tritone — resolving to the Cifra Club key as a
  structural/final cadence), with the criterion recorded in the justification. A **tonal**
  tier the `center_accuracy` runs over (`structural_offset = 0`).
- `chediak` — the center is taken from the book with a cited page. A `chediak`-**tonal**
  fact (`center_type = tonal`, e.g. Palco = Mi maior, p.194) feeds `center_accuracy` with a
  curated degree `structural_offset`; a `chediak`-**modal** fact (`center_type = modal`,
  e.g. Arrastão = A dorian, p.125) feeds the modal coverage + ledger with a curated
  `finalis_from_tonal` interval. Neither is absolute pitch subtraction.
- `unverified` — neither holds; the song is quarantined and excluded from both center metrics.

`structural_offset = 0` SHALL be a verified or Chediak-cited claim, NOT a default inherited
from the Cifra Club annotation. Tonal center accuracy SHALL be reported over the `verified`
∪ `chediak`-tonal subset, with the `chediak`-tonal subset size reported alongside so the
expanded coverage is visible and never silently blended with `verified`; the modal centers
over the `chediak` subset are reported as a coverage + ledger; the `unverified` count SHALL
be reported separately. Both reports are additive: the existing mode, exact, relative-aware,
and collection metrics are unchanged, and the `verified`-tier center value is unchanged.

#### Scenario: Center accuracy counts a wrong-degree detection as a miss
- **WHEN** the tonic is verified (offset 0) and the detection centers on another diatonic degree (e.g. the dominant V or the mediant iii) instead
- **THEN** the song does NOT count toward tonal center accuracy
- **AND** the Cifra Club exact/relative/collection metrics are computed exactly as before

#### Scenario: A Chediak-cited tonal center expands center coverage non-circularly
- **WHEN** a song has no functional-dominant verification but Chediak's Parte 4 cites its tonal center ("Tom de X"), and the detected center matches the curated degree offset
- **THEN** the song counts toward `center_accuracy` in the `chediak`-tonal tier
- **AND** the `verified`-tier center value and the four Cifra-Club metrics are unchanged
- **AND** the `chediak`-tonal subset size is reported alongside so the expanded coverage is visible

#### Scenario: The Chediak-tonal offset is a curated degree fact, not absolute subtraction
- **WHEN** Chediak's edition and the Cifra Club arrangement are in different transpositions (e.g. Chediak names Mi maior, the CC arrangement annotated Fá)
- **THEN** the `structural_offset` is the curated degree role of Chediak's tonic relative to the CC annotation (here, both name the tonic → `0`), not `(chediak_tom_pc − cifra_club_key_pc) % 12`
- **AND** a correct detection in the CC arrangement is not penalised by the transposition gap

#### Scenario: A Chediak-tonal detector disagreement is surfaced as a hole
- **WHEN** a `chediak`-tonal song's detected center does not match the cited center's curated offset
- **THEN** the song does NOT count toward `center_accuracy` and is listed in the per-song center hole with its Cifra Club key, curated offset, and detected center visible

#### Scenario: Modal centers are reported by the ledger, not the tonal accuracy
- **WHEN** a song's structural center diverges from the Cifra Club key (a modal final, non-zero offset, `center_type = modal`)
- **THEN** it is NOT scored by the tonal center accuracy (neither tonal tier)
- **AND** its Chediak center fact (provenance `chediak`, curated interval) is reported in the modal-center coverage + divergence ledger

#### Scenario: Center accuracy is invariant to transposition
- **WHEN** a song's chords and its Cifra Club key are both transposed by the same interval
- **THEN** the center-accuracy verdict for that song is unchanged
- **AND** this holds because the metric compares the detected-to-key offset, not absolute pitch

#### Scenario: Unverified songs are quarantined from center accuracy
- **WHEN** a song has neither a Chediak citation nor an independently verified functional-dominant resolution to its Cifra Club key
- **THEN** it is marked `unverified` and excluded from both center-accuracy tiers
- **AND** its count is reported separately so coverage is visible
- **AND** `structural_offset = 0` is never assumed for it by default

#### Scenario: Structural gold stores only facts, never the book's harmonizations
- **WHEN** the structural gold is committed to the repository
- **THEN** it contains only `(song, key, offset, center_type, mode, page)` facts
- **AND** no chord sheet, harmonization, or analysis table from the book is stored; chords are re-fetched from Cifra Club

### Requirement: Baseline reports tonal center accuracy and the center hole

When `scripts/key_baseline.py` runs, its aggregate output SHALL include a tonal
center-accuracy line alongside the mode, exact, relative-aware, and collection lines, over
the `verified` ∪ `chediak`-tonal subset, and SHALL report the `chediak`-tonal subset size
separately so the expanded (non-circular) coverage is visible and never silently blended
with `verified`. It SHALL list the per-song **center hole** — songs whose detected center is
a different diatonic degree than the structural center (a verified tonic detected as the V,
or a Chediak-cited center the detector disagrees with) — making the target for the future
tonal-center fix explicit. Adding the `chediak`-tonal tier SHALL NOT change the four
Cifra-Club metric values nor the `verified`-tier center value.

#### Scenario: Aggregate output includes the center-accuracy line
- **WHEN** the baseline runs
- **THEN** the aggregate metrics include a tonal center-accuracy line (over the `verified` ∪ `chediak`-tonal subset) alongside the four Cifra-Club metrics, with the `chediak`-tonal subset size shown
- **AND** the four Cifra-Club metric values and the `verified`-tier center value are unchanged by this addition

#### Scenario: The center hole is listed per song
- **WHEN** a song's detected center is not the structural center (a wrong diatonic degree, whether verified or Chediak-cited)
- **THEN** the per-song output lists it with the structural center and the detected center both visible

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

