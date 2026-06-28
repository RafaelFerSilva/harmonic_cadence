## ADDED Requirements

### Requirement: Modal center is an additive overlay, never a re-centering of the tonal analysis

The analyzer SHALL expose an optional `modal_center` annotation that names a **modal center** — a finalis (center note) plus a church mode (dorian, mixolydian, phrygian, aeolian, …) — for a piece whose true center is modal and diverges from the tonal reading. The annotation SHALL be strictly additive: it MUST NOT alter the key, mode, scale degrees, harmonic functions, cadence taxonomy, or any of the four Cifra-Club key metrics produced by `detect_key`. `detect_key` SHALL NOT be modified by this capability. The annotation SHALL be absent (`None`) by default.

This capability is distinct from `modal-coloring`: coloring names a *flavor* anchored to the tonal tonic and refuses to re-center, whereas this overlay names a *center* (the finalis) that may differ from the tonal tonic — but only as a parallel descriptive field, never by overwriting the tonal output.

#### Scenario: Modal center never changes the tonal reading
- **WHEN** a piece receives a `modal_center` annotation
- **THEN** its reported key, mode, scale degrees, harmonic functions, cadences, and the four Cifra-Club metrics are exactly those produced without the overlay
- **AND** the modal center appears only as an additional descriptive field

#### Scenario: A purely tonal piece gets no modal center
- **WHEN** a tonal piece (functional dominant resolving to its tonic, no modal-cadence-to-a-different-finalis) is analyzed
- **THEN** its `modal_center` is `None`

### Requirement: Modal center arbitration fires only under the conservative Chediak gate

The analyzer SHALL emit a `modal_center` ONLY when ALL of the following hold, reflecting Chediak's modal↔tonal criterion (Vol. I pp. 121-123) — the tonic is repose reached by a characteristic modal cadence, not by a functional dominant:

1. **Absence of a functional dominant** — no functional `V7`/`SubV7` (a real tritone, `Category.DOMINANT`) resolves to either the tonal tonic detected by `detect_key` OR the candidate finalis, in a structural/final position (the same mechanical criterion as `verify_tonal_center`).
2. **Modal cadence to the finalis** — a characteristic modal cadence (`bVII→I` mixolydian, `IV→i` dorian, `bII→i` phrygian, or the aeolian `v→i`/`bVII→i`) resolves onto the **finalis**, computed degree-relative to that finalis.
3. **Finalis distinct from the tonal tonic** — the bass-centric finalis (most frequent bass, with the first and last chord weighted, per `modal._central_pc`) differs from the K-S tonal tonic; when they coincide, the piece is already correctly centered and only a coloring (not a re-centering) is warranted.

When any condition fails, the analyzer SHALL emit no modal center and the tonal reading SHALL stand unchanged. The arbitration SHALL reuse `modal_coloring` evidence and the modal library (`modal.detect_mode`, `_central_pc`, `modal_cadences`) and SHALL NOT introduce a parallel modal subsystem.

#### Scenario: Arrastão receives a Lá-dorian modal center
- **WHEN** a piece has no functional dominant resolving to its tonal tonic, a modal cadence resolving onto a finalis a perfect fifth above the tonal tonic, and that finalis differs from the K-S tonic (Arrastão: tonal axis Ré, finalis Lá, A dorian)
- **THEN** a `modal_center` is emitted naming the finalis (Lá) and its church mode (dorian)
- **AND** the tonal key reported by `detect_key` is unchanged

#### Scenario: A functional dominant suppresses the modal center
- **WHEN** a piece contains a functional `V7`/`SubV7` resolving to its tonal tonic in a structural cadence
- **THEN** no `modal_center` is emitted, because the piece is tonally centered by a dominant
- **AND** the tonal reading stands

#### Scenario: A coincident finalis yields no modal center
- **WHEN** the bass-centric finalis coincides with the K-S tonal tonic (the piece is already centered there)
- **THEN** no `modal_center` is emitted (a `modal_coloring` flavor may still apply)

#### Scenario: Arbitration reuses existing modal machinery
- **WHEN** the modal center is computed
- **THEN** it is derived from `modal._central_pc` (finalis), `modal.detect_mode` / `modal_coloring` (mode and cadence evidence), and `verify_tonal_center` (absence of functional dominant)
- **AND** no new parallel modal-detection subsystem is introduced

### Requirement: Modal center carries finalis, mode, and cadence evidence; degrades visibly

The `modal_center` annotation SHALL report the finalis (center note, spelled via `Note`), the church mode, and the modal-cadence evidence that justified it (the characteristic degree and where it resolves to the finalis). The annotation SHALL be surfaced as a lazy analysis section that degrades **visibly** (`_safe_section` + `result["diagnostics"]`), never silently, consistent with the project's observability convention. Human-facing text SHALL be PT-BR (e.g. "Centro modal: Lá dórico"); the internal model SHALL use canonical English spelling.

#### Scenario: Modal center reports finalis, mode, and evidence
- **WHEN** a `modal_center` is emitted
- **THEN** it contains the finalis note, the church mode, and the cadence evidence (characteristic degree resolving to the finalis)

#### Scenario: Modal-center section degrades visibly on error
- **WHEN** the modal-center section raises during analysis
- **THEN** the failure is recorded in `result["diagnostics"]` and the rest of the analysis is unaffected
- **AND** the section is not silently dropped
