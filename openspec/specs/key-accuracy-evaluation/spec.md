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

This requirement covers the **tonal** center only (`structural_offset = 0`, the Cifra Club
key confirmed as the true tonic). **Modal** centers, where the structural center diverges
from the Cifra Club key (non-zero offset, e.g. Arrastão = A dorian), are OUT OF SCOPE here
and deferred to the modal-arbitration change: their offset cannot be derived by absolute
pitch subtraction, because Chediak's analysis and the Cifra Club arrangement may be in
different transpositions (e.g. Chediak analyses "Pra não dizer…" in E aeolian while the
Cifra Club arrangement is in F minor — absolute subtraction would penalise a correct
detection). The modal change derives the offset from the modal final's scale degree within
the collection, not from absolute pitch.

The structural gold SHALL be a committed list of **facts** — `(song, cifra_club_key,
structural_offset, center_type, mode, provenance, justification)` — never the book's
harmonizations, chord tables, or chord sheets. Each entry SHALL carry a **provenance**
tier, because the Cifra Club key is a transposition anchor, NOT an authoritative source of
the tonal center:

- `verified` — the center is independently confirmed by a documented mechanical criterion
  (a functional dominant — a true V7 tritone — resolving to the Cifra Club key as a
  structural/final cadence), with the criterion recorded in the justification. This is the
  tier the tonal center metric runs over (`structural_offset = 0`).
- `chediak` — the center is taken from the book with a cited page (e.g. Arrastão = A
  dorian, p.125). These facts are committed as the authoritative, non-circular anchor for
  the future modal-arbitration change, but are NOT used in this change's tonal metric.
- `unverified` — neither holds; the song is quarantined and excluded from center accuracy.

`structural_offset = 0` SHALL be a verified claim (provenance `verified`), NOT a default
inherited from the Cifra Club annotation. Center accuracy SHALL be reported over the
`verified` subset only; the `unverified` count SHALL be reported separately so coverage is
visible. Center accuracy is additive: the existing mode, exact, relative-aware, and
collection metrics are unchanged.

#### Scenario: Center accuracy counts a wrong-degree detection as a miss
- **WHEN** the tonic is verified (offset 0) and the detection centers on another diatonic degree (e.g. the dominant V or the mediant iii) instead
- **THEN** the song does NOT count toward center accuracy
- **AND** the Cifra Club exact/relative/collection metrics are computed exactly as before

#### Scenario: Modal centers are excluded from this change's metric
- **WHEN** a song's structural center diverges from the Cifra Club key (a modal final, non-zero offset)
- **THEN** it is NOT scored by this change's tonal center accuracy
- **AND** its Chediak center fact is committed (provenance `chediak`) for the future modal-arbitration change

#### Scenario: Center accuracy is invariant to transposition
- **WHEN** a song's chords and its Cifra Club key are both transposed by the same interval
- **THEN** the center-accuracy verdict for that song is unchanged
- **AND** this holds because the metric compares the detected-to-key offset, not absolute pitch

#### Scenario: Unverified songs are quarantined from center accuracy
- **WHEN** a song has neither a Chediak citation nor an independently verified functional-dominant resolution to its Cifra Club key
- **THEN** it is marked `unverified` and excluded from the center-accuracy denominator
- **AND** its count is reported separately so coverage is visible
- **AND** `structural_offset = 0` is never assumed for it by default

#### Scenario: Structural gold stores only facts, never the book's harmonizations
- **WHEN** the structural gold is committed to the repository
- **THEN** it contains only `(song, key, offset, center_type, mode, page)` facts
- **AND** no chord sheet, harmonization, or analysis table from the book is stored; chords are re-fetched from Cifra Club

### Requirement: Baseline reports tonal center accuracy and the center hole

When `scripts/key_baseline.py` runs, its aggregate output SHALL include a tonal
center-accuracy line alongside the mode, exact, relative-aware, and collection lines, and
SHALL list the per-song **center hole** — the verified songs whose detected center is a
different diatonic degree (e.g. the dominant V detected as tonic) — making the target for
the future tonal-center fix explicit.

#### Scenario: Aggregate output includes the center-accuracy line
- **WHEN** the baseline runs
- **THEN** the aggregate metrics include a tonal center-accuracy line (over the verified subset) alongside the four Cifra-Club metrics
- **AND** the four Cifra-Club metric values are unchanged by this addition

#### Scenario: The center hole is listed per song
- **WHEN** a verified song's detected center is not the true tonic (a wrong diatonic degree)
- **THEN** the per-song output lists it with the true tonic and the detected center both visible

