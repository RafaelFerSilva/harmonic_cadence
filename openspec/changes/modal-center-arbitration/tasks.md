> **REDESIGNED FOR CAMINHO 2 — ANNOTATION (2026-06-29).** Group 1 (the trava) ran and
> invalidated the original detection design (Caminho 1): the Chediak modal center is not
> encoded in the Cifra Club chords. Groups below are the **Caminho 2** plan — curated
> annotation at display time, no detection. See [design.md](./design.md) and
> [PROBE-FINDINGS.md](./PROBE-FINDINGS.md). NOT yet implemented.

## 1. Capture the live baseline (the trava) — DONE

- [x] 1.1 Run `uv run python scripts/key_baseline.py` and record the four Cifra-Club metrics, the tonal `center_accuracy`, and the modulating numbers verbatim (zero-regression reference).
- [x] 1.2 Probe the four `chediak`-tier songs — **finding: detection premise invalidated** (Arrastão finalis→Mi not Lá; Procissão Dó absent; Upa/Pra-Não-Dizer center already correct, only mode-name diverges → that is part (A)). Recorded in PROBE-FINDINGS.md.

## 2. Curated-source format & location — DECIDED (D2, Appendix A)

- [x] 2.1 **Decided:** a typed Python module at `packages/harmonic_analysis/src/harmonic_analysis/corpus/modal_centers.py` (single source, test-visible, importable by both validation and presentation; `scripts/` is unlinted and needs a path hack). Typed contract in design.md Appendix A.
- [ ] 2.2 **OPEN (separate decision):** promote mypy to the gate? Adding `uv run mypy` to `make lint` (+ extend ruff/mypy to `scripts/`) would make `Literal[ChurchMode]` + no-default citation static-CI-enforced, not IDE-only. Orthogonal to this change.

## 3. Single curated modal-center dataset (promote TIER_A_CHEDIAK)

- [ ] 3.1 Create the typed module per Appendix A: `Citation` (frozen, kw_only, `__post_init__` validates source/volume/page) + `ModalCenterFact` (frozen, kw_only, `citation` required no default, `curated_mode: Literal[ChurchMode]`, `finalis_from_tonal` range-checked) + `CORPUS` tuple. **Migrate** `scripts/chediak_structural_gold.py::TIER_A_CHEDIAK` to read from it (no duplicate copy — honor "uma fonte").
- [ ] 3.2 Populate **center-divergence cases only** (offset ≠ 0): Arrastão (Lá dórico, p.125), Procissão (Dó mixolídio, p.126). EXCLUDE Upa Neguinho / Pra Não Dizer (center already correct → part (A)).
- [ ] 3.3 Each entry's `finalis_from_tonal` is the curated interval finalis−(detected tonal center) read onto the scraped chords (D5) — NEVER `chediak_center_pc − cc_key_pc`; cite the page + record the reasoning in `note`. Facts only (no chords, no book text).
- [ ] 3.4 Add the **corpus invariant test** (`tests/test_modal_corpus.py`, Appendix A): every fact has a valid `Citation`; constructing a `ModalCenterFact` without `citation` raises `TypeError`. This is the build gate that makes the citation structurally mandatory.

## 4. Identity-keyed lookup (presentation)

- [ ] 4.1 Add a lookup keyed by `slug(artist)|slug(song)` reusing [`cifra_core/slug.py`](packages/cifra_core/src/cifra_core/slug.py); a miss returns None (no note).
- [ ] 4.2 Unit-test identity matching: "Arrastao"/"Arrastão", artist casing variants resolve; an unknown song misses cleanly.

## 5. Curator-note render (markdown + html), display-only — see Appendix B

- [ ] 5.0 Add `format_citation(citation)` to `presentation/labels.py` (single source of the citation string: "Almir Chediak, Harmonia & Improvisação, Vol. I, p. 125"; Roman volume) so MD and HTML never diverge. Unit-test it.
- [ ] 5.1 In `presentation/reports/markdown.py` `_generate_header`: when a curated entry matches, render the "Nota do curador" **blockquote immediately below "Centro modal"** (Appendix B) — Chediak's modal center + arrangement-divergence caveat (D5.2) + the citation as the attribution last line. Omit entirely on a miss (report byte-identical to today).
- [ ] 5.2 In `presentation/reports/html.py` `_generate_html_document`: parity — a Bootstrap `alert` callout with the semantic `<cite>` element + `blockquote-footer` citation (Appendix B), placed right after the "Centro modal" `<p>`.
- [ ] 5.3 (Optional, D5.2) also show the transposition-safe relative finalis ("dórico sobre o Nº grau da leitura tonal") via `finalis_from_tonal`.
- [ ] 5.4 Purity: the render reads only the curated dataset + analysis identity; it never touches `detect_key`/`detect_coloring` nor mutates the analysis JSON. JSON report carries the structured `citation` (source/volume/page), not the assembled string.

## 6. Coverage + divergence ledger (NOT detection accuracy, D6)

- [ ] 6.1 In `validation/key_accuracy.py`: add a modal-center **coverage** count + **divergence ledger** over the curated set — per song `(detected tonal center, curated center+mode, finalis_from_tonal, page)`. NO accuracy % (nothing is detected). Keep the tonal `center_accuracy` (verified tier) and the four Cifra-Club metrics byte-identical.
- [ ] 6.2 Transposition-safety test: the ledger uses the curated interval, not absolute subtraction — a fabricated Chediak-vs-CC transposition gap does not corrupt the ledger entry.

## 7. Baseline reporting + the inviolable trava

- [ ] 7.1 Add the modal-center coverage + ledger line to `scripts/key_baseline.py`, alongside the tonal center block; report n/coverage so it is never overstated.
- [ ] 7.2 Run `uv run python scripts/key_baseline.py` live; **diff** the four Cifra-Club metrics and the tonal `center_accuracy` against task 1.1 — must be IDENTICAL (zero regression, inviolable).

## 8. Quality gate + docs + specs

- [ ] 8.1 Regenerate the `specs/` deltas for Caminho 2 (the current ones describe Caminho 1 detection) — `modal-center-arbitration` (annotation capability) + `key-accuracy-evaluation` (coverage/ledger, not accuracy). `openspec validate modal-center-arbitration --strict` passes.
- [ ] 8.2 `make test` green; `make lint` clean.
- [ ] 8.3 Update `ROADMAP.md`/`AGENTS.md`: mark `modal-center-arbitration` (part B) done via Caminho 2; the bifurcation (A)+(B) complete; coverage n + zero tonal regression. Then `openspec archive`.
