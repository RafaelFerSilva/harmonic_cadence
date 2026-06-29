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
