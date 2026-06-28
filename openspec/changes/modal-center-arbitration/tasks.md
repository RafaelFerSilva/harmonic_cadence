> **HALTED AFTER TASK 1 — BLOCKED BY DATA (2026-06-28).** Group 1 (the trava) ran and
> invalidated the design premise: the Chediak modal center is not encoded in the Cifra Club
> chords. See [PROBE-FINDINGS.md](./PROBE-FINDINGS.md) and the proposal's STATUS banner.
> Groups 2–8 are NOT implemented; reopen only with a curated modal corpus.

## 1. Capture the live baseline (the trava)

- [x] 1.1 Run `uv run python scripts/key_baseline.py` and record the current four Cifra-Club metrics, the tonal `center_accuracy`, and the modulating numbers verbatim — baseline: modo 86 · exata 69 · relativa 76 · coleção 97 · centro TONAL 79 (15/19) · modulantes 100.
- [x] 1.2 Probe the four `chediak`-tier songs — **finding: design premise invalidated** (Arrastão finalis→Mi not Lá; Procissão Dó absent; Upa/Pra-Não-Dizer center already correct, only mode-name diverges). Recorded in PROBE-FINDINGS.md.

## 2. Modal-center arbitration overlay (domain)

- [ ] 2.1 Create `packages/harmonic_analysis/src/harmonic_analysis/domain/modal_center.py` with a frozen `ModalCenter` dataclass (`finalis_pc`, `finalis_note`, `mode`, `evidence`, `where`) and `arbitrate_modal_center(symbols, tonal_tonic_pc, tonal_mode) -> Optional[ModalCenter]`.
- [ ] 2.2 Implement gate conjunct 1 (absence of functional dominant): reuse `chediak_structural_gold.verify_tonal_center` against BOTH the tonal tonic and the candidate finalis; abort (return None) if either resolves.
- [ ] 2.3 Implement gate conjunct 2 (modal cadence to finalis): reuse `modal._central_pc` for the finalis and `modal.modal_cadences` / the `modal_coloring._cadence_to_tonic` shape to confirm a characteristic degree resolves onto the finalis; record the evidence + `where`.
- [ ] 2.4 Implement gate conjunct 3 (finalis ≠ tonal tonic): abort when `_central_pc(symbols) == tonal_tonic_pc` (already centered → coloring, not re-centering).
- [ ] 2.5 Classify the church mode by calling `modal.detect_mode` behind the gate; spell the finalis via `Note`; assemble `ModalCenter`. Reuse machinery only — introduce no parallel modal subsystem.
- [ ] 2.6 Guarantee purity: the function reads `symbols` only and returns an overlay value; it never calls or mutates `detect_key`.

## 3. Domain tests

- [ ] 3.1 `packages/harmonic_analysis/tests/test_modal_center.py`: Arrastão-shaped input (no functional dominant, modal cadence onto a finalis a 5th above the tonal axis, finalis ≠ tonic) yields a dorian `ModalCenter` on the finalis.
- [ ] 3.2 A piece with a functional `V7`/`SubV7` → tonic yields `None` (dominant suppresses the overlay).
- [ ] 3.3 A coincident finalis (== tonal tonic) yields `None`.
- [ ] 3.4 Silence cases: plain aeolian pieces (Wave/Corcovado/Insensatez-shaped) and a diatonic major (`C F G7 C`) yield `None` — the false-phrygian trap stays shut.
- [ ] 3.5 Assert the overlay performs no re-centering: the tonal `detect_key` result for the same symbols is unchanged whether or not `arbitrate_modal_center` is called.

## 4. Report integration (analysis_service)

- [ ] 4.1 Add a lazy `modal_center` section in `services/analysis_service._add_depth_sections` (mirroring the `modal_coloring` wiring), passing the tonal tonic/mode + symbols, wrapped in `_safe_section` so failures land in `result["diagnostics"]`.
- [ ] 4.2 Render PT-BR human text (e.g. "Centro modal: Lá dórico") with the cadence evidence; keep the internal model in canonical English.
- [ ] 4.3 Test that the section degrades visibly on error and that a tonal piece produces no `modal_center` field.

## 5. Degree-relative modal center metric (validation harness)

- [ ] 5.1 Extend the structural gold in `scripts/chediak_structural_gold.py`: add a curated `degree_offset` (the finalis's degree relative to the Cifra Club key, per Chediak's functional reading) to each `chediak`/modal fact — NOT derived by `chediak_center_pc − cc_key_pc`. Cite the page + record the degree relationship in the justification.
- [ ] 5.2 In `validation/key_accuracy.py`, add `modal_center_accuracy` to `evaluate_corpus`: run `center_ok(detected_center, cc_key, curated_offset)` over the `chediak` provenance subset, using the modal-center finalis as `detected_center`; keep the tonal `center_accuracy` (verified tier) and the four Cifra-Club metrics byte-identical.
- [ ] 5.3 Report the `chediak`-subset size alongside the metric so coverage is visible; quarantine unchanged.

## 6. Harness tests

- [ ] 6.1 In `packages/harmonic_analysis/tests/test_key_accuracy.py`: a correct modal center (Arrastão: finalis Lá, cc_key Ré, curated offset +7) counts toward `modal_center_accuracy`.
- [ ] 6.2 Transposition invariance: transpose chords + cc_key by the same interval → modal verdict unchanged.
- [ ] 6.3 The curated offset is NOT absolute subtraction: a fabricated Chediak-vs-CC transposition gap (E vs F) still scores a correct detection as a hit.
- [ ] 6.4 The four Cifra-Club metrics and the tonal `center_accuracy` are unchanged by adding the modal metric.

## 7. Baseline reporting + live verification

- [ ] 7.1 Add the `modal_center_accuracy` line + per-song modal-hole list to `scripts/key_baseline.py`, alongside the existing tonal center block.
- [ ] 7.2 Run `uv run python scripts/key_baseline.py` live; confirm the four Cifra-Club metrics and the tonal `center_accuracy` are IDENTICAL to task 1.1 (zero regression — inviolable).
- [ ] 7.3 Decide aeolian scope from the live numbers (open question in design): ship only the flavors that gate cleanly without adding relative-minor noise; document any deferral.

## 8. Quality gate + docs

- [ ] 8.1 `make test` green; `make lint` clean.
- [ ] 8.2 Update `ROADMAP.md`: mark `modal-center-arbitration` done, record the new `modal_center_accuracy` and confirm the four Cifra-Club metrics + tonal center unchanged; update the n/coverage line.
- [ ] 8.3 `openspec validate modal-center-arbitration --strict` passes; ready for `openspec archive`.
