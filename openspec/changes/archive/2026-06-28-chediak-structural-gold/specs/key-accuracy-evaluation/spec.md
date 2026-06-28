## ADDED Requirements

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
