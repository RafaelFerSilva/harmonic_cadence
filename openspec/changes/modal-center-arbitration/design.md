## Context

The Fase B center stack (cadential tiebreak v1, parallel-mode correction v2, tuning
filter v3, 3b tritone quality gate) is mature and all of it is **tonal**: every
mechanism either trusts or corrects toward a center reached by a **functional dominant**.
The 3b gate (`_tritone_gate`, [key_detection.py:213](packages/harmonic_analysis/src/harmonic_analysis/domain/key_detection.py#L213))
is explicit about this — it fires only when the K-S guess appears *exclusively as a
dominant-7 resolving down a fifth to a resting chord*. A modal piece has **no functional
dominant by construction**, so none of these mechanisms can find its center, and the
`center_accuracy` metric runs only over the dominant-`verified` subset
([key_accuracy.py:207](packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py#L207)),
which quarantines every modal piece.

Meanwhile the modal facts already exist as cited authority but are inert:
`TIER_A_CHEDIAK` in [chediak_structural_gold.py:37](scripts/chediak_structural_gold.py#L37)
lists Arrastão (A dorian, p.125), Upa Neguinho (D mixolydian, p.126), Procissão (C
mixolydian, p.126), Pra Não Dizer (E aeolian, p.127) — explicitly "RESERVADO para a change
2", because their offset cannot be derived by absolute subtraction. The `modal_coloring`
overlay ([modal_coloring.py](packages/harmonic_analysis/src/harmonic_analysis/domain/modal_coloring.py))
already reads the borrowings and names a flavor, but is contractually forbidden from
re-centering. The modal library ([modal.py](packages/harmonic_analysis/src/harmonic_analysis/domain/modal.py))
has `_central_pc` (bass-centric finalis), `detect_mode` (church-mode classification), and
`modal_cadences` — but `detect_mode` was deliberately removed from the pipeline
(`fix-or-remove-church-mode`) because auto-promotion produced 12/60 spurious phrygians.

This change closes the loop: an **overlay** (not a pipeline re-centering) that names the
modal center under a gate strict enough to avoid the spurious-phrygian trap, plus the
**degree-relative metric** that finally measures it. Constraints: `detect_key` is
untouched; the four Cifra-Club metrics and the tonal `center_accuracy` stay byte-identical;
every recalibration is measured live against the baseline (the rule that already barred two
bad ships — see [[tritone-gate-quality-lesson]]).

## Goals / Non-Goals

**Goals:**
- Name a modal center (finalis + church mode) for Arrastão-class pieces, as an additive
  overlay distinct from the tonal key.
- Gate it on Chediak's principled criterion (pp. 121-123): absence of a functional
  dominant + a characteristic modal cadence resolving onto a finalis that differs from
  the K-S tonic.
- Reuse existing machinery (`modal._central_pc`, `detect_mode`, `modal_cadences`,
  `modal_coloring`, `verify_tonal_center`) — no parallel modal subsystem.
- Add a degree-relative `modal_center_accuracy` metric over the existing `chediak` tier,
  with curated degree offsets, and report it live in the baseline.

**Non-Goals:**
- Modifying `detect_key` or any tonal metric (inviolable: zero regression).
- Re-centering the tonal analysis or re-introducing auto modal promotion into the
  pipeline.
- Solving the 4 remaining tonal V-as-tonic cases (A Banda / Aquele Abraço / Apesar de
  Você / Menino do Rio) — those stay with the tonal gate frontier.
- dim7-as-dominant (viio7 = V7b9) — its own future change.
- Curating a large modal corpus; the metric runs over the ~4 committed `chediak` facts
  and grows later.

## Decisions

### D1 — Overlay module, not a `detect_key` change

Add `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_center.py` exposing
`arbitrate_modal_center(symbols, tonal_tonic_pc, tonal_mode) -> Optional[ModalCenter]`,
called as a lazy section in `analysis_service` exactly like `modal_coloring`
([analysis_service.py:408](packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py#L408)).

*Why over extending `detect_key`*: the ROADMAP's "bloqueado" warning is precise — the
center failure spreads over V/vi/iii/IV with no single safe gate, and any re-centering
risks the ~41 correct tonal detections. An overlay carries **zero** risk to the tonal
metrics by construction. *Why over extending `modal_coloring`*: coloring's contract is
"anchored to the tonal tonic, never re-center"; naming a different finalis is a different
concern. It *reuses* coloring's evidence helpers but lives separately.

### D2 — The gate: absence-of-dominant ∧ modal-cadence-to-finalis ∧ finalis≠tonic

Three conjuncts, all from existing code:
1. **Absence of functional dominant** — `not verify_tonal_center(symbols, tonal_tonic_pc)`
   **and** `not verify_tonal_center(symbols, finalis_pc)`. Reuses the Tier-B mechanical
   criterion (true tritone `Category.DOMINANT` resolving in a final cadence,
   [chediak_structural_gold.py:68](scripts/chediak_structural_gold.py#L68)). This is the
   single hardest gate — a piece with a real V7→I is tonal, full stop (Chediak p.84/87).
2. **Modal cadence to the finalis** — the characteristic degree of the candidate mode
   resolves onto the finalis, computed degree-relative to the **finalis** (reusing the
   `modal_coloring._cadence_to_tonic` / `modal.modal_cadences` shape). This is what
   distinguishes a genuine modal close from incidental chromaticism.
3. **Finalis ≠ tonal tonic** — `_central_pc(symbols) != tonal_tonic_pc`. When they
   coincide the piece is already centered; only a coloring is warranted, not a
   re-centering.

*Why this triple and not statistics*: [[tritone-gate-quality-lesson]] — MPB's secondary-
dominant density defeats collection/statistical discriminators; only the **functional**
signal (repose vs. tension, dominant resolution) survives. Absence-of-dominant is the
negative of that same functional signal, so it inherits the robustness.

### D3 — Church mode from `detect_mode`, finalis-anchored

Once the gate passes, classify the mode by calling `detect_mode(symbols)`
([modal.py:122](packages/harmonic_analysis/src/harmonic_analysis/domain/modal.py#L122)),
which already derives the church mode from the collection + finalis. We trust it **only
behind the gate** — the very gate whose absence made `detect_mode` produce 12/60 false
phrygians when run unconditionally. The conjunction (no dominant + modal cadence + finalis
shift) is exactly the missing precondition.

### D4 — Metric: curated degree offset over the `chediak` tier, one frame

`modal_center_accuracy` reuses `center_ok(detected, cc_key, structural_offset)`
([key_accuracy.py:73](packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py#L73))
unchanged — it already compares `(detected − cc_key) % 12 == offset`. The only new thing is
**where the gold offset comes from**: a curated degree fact per modal song, not
`structural_offset(center_note, cc_key_pc)` (the absolute subtraction at
[chediak_structural_gold.py:56](scripts/chediak_structural_gold.py#L56), which is unsafe
across transpositions). We extend `TIER_A_CHEDIAK` entries (or a parallel modal map) with a
hand-curated `degree_offset` taken from Chediak's functional reading, and run
`evaluate_corpus`'s center branch over the `chediak` provenance using that offset. Both
operands of `center_ok` come from the Cifra Club arrangement → transposition-invariant.

*Why curated, not derived*: see [[center-eval-degree-relative]] — the metric must compare
degrees in **one** frame `(detected − cc_key) % 12`; the Chediak note is in a possibly
different frame, so subtracting it cross-frame is the documented bug (Pra Não Dizer E vs F).
The degree relationship ("the finalis is the V of the CC key") *is* frame-invariant and is
the curatable fact.

### D5 — Report & observability

`analysis_service` gets a lazy `modal_center` section via `_safe_section` (visible
degradation + `result["diagnostics"]`). `scripts/key_baseline.py` gains a
`modal_center_accuracy` line + per-song modal-hole list, alongside the existing tonal
center block, measured live. Human text PT-BR ("Centro modal: Lá dórico"); internal model
canonical English.

## Risks / Trade-offs

- **[Re-centering leaks into the tonal output]** → The overlay never writes key/mode;
  enforced by a spec scenario ("Modal center never changes the tonal reading") and a test
  asserting the four metrics + tonal `center_accuracy` are byte-identical before/after.
- **[`detect_mode` false-positive resurfacing]** → It runs *only* behind the three-conjunct
  gate; tests cover the silence cases (eólias Wave/Corcovado/Insensatez must get no modal
  center; a diatonic major must get none).
- **[Tiny metric n (~4 chediak facts)]** → Honest and additive; reported with its subset
  size so coverage is visible. Not a quality gate on its own — it measures the new
  arbitration, it does not block the four tonal metrics. Grows as the modal corpus grows.
- **[Curated offset is a manual judgement]** → Each offset cites a Chediak page and records
  the degree relationship in the justification; it is a fact, not a tuning knob. Copyright
  wall holds: facts only (song→center→mode→page), never harmonizations (see
  [[baseline-gold-is-cifraclub]]).
- **[Aeolian is "just" the relative minor]** → Pra Não Dizer (E aeolian) overlaps the tonal
  relative-minor reading; the overlay should add value only when the finalis genuinely
  shifts the center. Guarded by conjunct 3 (finalis ≠ tonic) and validated against the
  baseline; if it produces noise, scope the first ship to dorian/mixolydian and defer
  aeolian.

## Migration Plan

1. Land `modal_center.py` + tests (overlay, no pipeline wiring) — baseline unchanged.
2. Wire the lazy `analysis_service` section behind `_safe_section`.
3. Extend the structural gold with curated `degree_offset` + activate the `chediak` tier in
   the metric; add the baseline line.
4. Run `uv run python scripts/key_baseline.py` live; confirm the four Cifra-Club metrics
   and tonal `center_accuracy` are identical; record `modal_center_accuracy` in ROADMAP.
5. Rollback = drop the overlay call + metric line; `detect_key` was never touched, so the
   tonal baseline is the rollback target by construction.

## Open Questions

- Does the first ship include **aeolian** (Pra Não Dizer) or scope to dorian/mixolydian
  until the finalis-shift heuristic is proven not to add relative-minor noise? Lean:
  measure all four against the baseline; ship only the flavors that gate cleanly.
- Should `modal_center` and `modal_coloring` ever co-occur on one piece, and if so how is
  the PT-BR report worded? Lean: allow both (center names the finalis, coloring the
  borrowings); resolve wording at report time.
