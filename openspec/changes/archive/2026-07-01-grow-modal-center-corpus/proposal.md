## Why

A change `modal-center-arbitration` shipped the full machinery for curated modal-center
annotations (typed corpus with mandatory citation, identity lookup, curator note in
MD/HTML/JSON, coverage + divergence ledger) but seeded it with only **n=2** facts
(Arrastão p.125, Procissão p.126) — the architecture is the deliverable, the facts accrue.
The feature is correct but low-coverage: most modal MPB pieces Chediak analyzes as
center-divergent still read on the tonal axis with no curator note. Growing the corpus is
the highest-leverage, lowest-risk next step: it is **pure curation** that reuses everything
already built, adds zero detection risk, and turns each new fact into a music lesson.

## What Changes

- Add **more curated modal-center facts** to `harmonic_analysis.corpus.modal_centers.CORPUS`,
  each a genuine **center divergence** (the finalis differs from the detected tonal center,
  `finalis_from_tonal != 0`), drawn from Chediak Vol. I (Parte 2, the modal section
  pp.121-127 and any cited modal analysis elsewhere in the volume). Facts only
  (center/mode/`finalis_from_tonal`/page/note) — never chords or book text.
- Formalize a **fact-admission protocol** so the corpus stays trustworthy as it grows: a
  candidate becomes a committed fact only after a documented live check — scrape the Cifra
  Club chords, run `detect_key` to fix the arrangement's tonal axis, confirm the center
  genuinely diverges (offset ≠ 0; mode-name-only divergences stay with part (A) and are
  rejected), curate `finalis_from_tonal` by reading Chediak's analysis onto the scraped
  chords (NEVER `chediak_pc − cc_key_pc`), cite the page, and re-run the baseline to prove
  zero tonal regression.
- Each new fact's identity (artist + title) must slug-match what the in-process provider
  scrapes; unresolved/404 candidates are deferred, not guessed.

## Capabilities

### New Capabilities
<!-- none — this change adds data + a curation protocol to an existing capability -->

### Modified Capabilities
- `modal-center-arbitration`: add a **fact-admission protocol** requirement — the documented
  live-verification gate every new curated fact must pass (center-divergence confirmed,
  `finalis_from_tonal` curated not subtracted, page cited, zero tonal regression), so the
  corpus can grow without eroding trust or the inviolable baseline.

## Impact

- **New data:** additional `ModalCenterFact` entries in
  `packages/harmonic_analysis/src/harmonic_analysis/corpus/modal_centers.py` (the single
  source; `TIER_A_CHEDIAK` already reads from it).
- **New tests:** extend `tests/test_modal_centers_corpus.py` — invariants already
  parametrize over `CORPUS`, so they cover new facts automatically; add identity-resolution
  assertions for each new song and (optionally) per-fact divergence assertions.
- **Reuses unchanged:** the lookup, the curator-note renders (MD/HTML/JSON), `format_citation`,
  `interval_pt`, and the `modal_center_ledger` — all iterate `CORPUS`, so they pick up new
  facts with no code change. The baseline ledger block already reports coverage live.
- **Does NOT touch:** `detect_key`, `detect_coloring`, any tonal metric, or the four
  Cifra-Club metrics. Pure curation/data front.
- **Risk gate:** zero regression of the four Cifra-Club metrics and the tonal
  `center_accuracy`, proven live against the baseline — same inviolable trava as the parent
  change.
- **Constraint:** requires Chediak Vol. I (`base_estudo/`, gitignored) to source pages and
  network to scrape candidate chords; coverage grows fact-by-fact, never by guessing.
