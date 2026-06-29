## Context

`center_accuracy` today runs over the `verified` tier only — 19 songs where a functional
dominant resolves to the Cifra Club key (`verify_tonal_center`, `scripts/chediak_structural_gold.py`).
The other ~41 corpus songs are `unverified` and quarantined. The harness already carries the
full machinery for a second tier: `KeyEval.structural_offset`, `center_ok(detected, cc_key,
offset)` (degree-relative, transposition-invariant), and `evaluate_corpus(structural=...)`
keyed by `nome → (offset, provenance)`. The `chediak` provenance string already exists; after
`modal-center-arbitration` it feeds the modal ledger. Chediak's Parte 4 heads every analyzed
song with **"Tom de X maior/menor"** (verified live: "PALCO" → Mi maior) — a cited, independent
tonal-center fact we are not yet using.

Golden Rule constraints: the Cifra Club key is a **transposition anchor**, not the truth; only
**facts** (song → tom → page) cross the copyright wall, never the harmonizations. The metric is
**degree-relative** in the single `(detected − cc_key) % 12` frame ([[center-eval-degree-relative]]).

## Goals / Non-Goals

**Goals:**
- Add a `chediak`-**tonal** tier to the structural-center gold from Parte 4's "Tom de X" labels,
  feeding the existing degree-relative `center_accuracy` over `verified` ∪ `chediak-tonal`.
- Expand center coverage past 19 with a **non-circular** anchor (independent of a dominant) and
  **surface detector holes** where `detect_key` disagrees with the cited center.
- Keep the offset **curated degree-relative**, transposition-safe; never absolute subtraction.
- Zero regression of the four Cifra-Club metrics and the current `verified`-tier value.

**Non-Goals:**
- Any change to `detect_key` (this measures it, exposing holes; fixing them is later work).
- The modal `CORPUS`/ledger (untouched; `chediak`-modal still feeds the ledger).
- Ingesting Parte 4 harmonizations/chord tables — facts only.
- A coverage quota — facts accrue page-by-page; the change succeeds at any added n ≥ 1.

## Decisions

### D1 — `center_type` splits the `chediak` tier: tonal → accuracy, modal → ledger

The structural fact already carries a `center_type` (tonal/modal). Route by it:
`provenance == chediak AND center_type == tonal` → the degree-relative `center_accuracy`;
`provenance == chediak AND center_type == modal` → the modal ledger (unchanged). `verified`
stays tonal/offset-0. So `center_accuracy` runs over `verified` ∪ `chediak-tonal`; the modal
facts never enter an accuracy. *Alternative rejected*: a brand-new metric name for chediak-tonal
— needless; it is the same degree-relative center judgment, just a different provenance of the
gold, so it belongs in the same metric with the subset size reported.

### D2 — The offset is a curated DEGREE relationship, not `chediak_tom_pc − cc_key_pc` (the crux)

Chediak's "Tom de X" lives in **his** edition; the scraped CC arrangement may be transposed.
We never subtract absolute pitches across the two sources. Instead we curate, per song, the
**role** Chediak's tonic plays relative to the CC annotation — a transposition-invariant degree:

```
CC annotated the tonic (same role, any transposition)      → structural_offset = 0
CC annotated the RELATIVE minor of Chediak's major tonic    → structural_offset = +3
CC annotated the RELATIVE major of Chediak's minor tonic    → structural_offset = -3 (= 9)
CC annotated some other degree (rare)                        → that degree's offset
```

Why this is sound: `center_ok` compares `(detected − cc_key) % 12` to the offset; both operands
live in the **arrangement's** pitch space, so any transposition of the arrangement cancels.
Chediak's contribution is purely the *role* ("this CC label names the real tonic / names the
relative / …"), which transposition cannot change. The relative relationship is the fixed ±3 of
the [[baseline-gold-is-cifraclub]] relative confusion. *Alternative rejected*: auto-deriving the
offset from `Note.parse(chediak_tom)` minus `cc_key` — the exact Mi-vs-Fá trap that breaks on
transposition; forbidden by [[center-eval-degree-relative]].

### D3 — Curation procedure per song (mirrors the modal `finalis_from_tonal` worksheet)

For each Parte 4 song with a "Tom de X" label and a scrapable CC chart: scrape → read `cc_key`
→ compare Chediak's tonic role to the CC annotation. Same pitch class → offset 0 (the common
case: CC usually annotates the tonic, Chediak confirms it non-circularly). Different label →
judge tonic-vs-relative-vs-transposition from Chediak's analysis and the arrangement, and record
the degree offset. The live baseline prints `(detected, cc_key, chediak_tom, offset, page)` per
fact as the curation check, exactly as the modal ledger does. Unresolvable (404 / ambiguous) →
defer, never guess.

### D4 — Where the facts live

Add the `chediak`-tonal facts beside the existing tiers in `scripts/chediak_structural_gold.py`
(a typed list `(artist, song, chediak_tom, structural_offset, page)`), and build the structural
map in `scripts/key_baseline.py` from `verified` (live `verify_tonal_center`, offset 0) ∪
`chediak-tonal` (curated). `evaluate_corpus` already accepts `structural: nome → (offset,
provenance)`; pass `provenance="chediak"` for the harvested songs. The `verified` path is
untouched, so its 19/19 cannot move. *Open*: whether to also expose these via the typed
`harmonic_analysis.corpus` package (like the modal `CORPUS`) for runtime import — deferred; the
baseline + validation harness are the only consumers today, and `scripts/` already owns the
tonal gold.

### D5 — Coverage honesty + the bug-surfacing hole

Report the `chediak`-tonal subset size alongside `center_accuracy` (so a higher denominator is
visible, never silently blended with `verified`). List the per-song **center hole**: chediak-
tonal songs where `(detected − cc_key) % 12 != structural_offset` — these are the detector
disagreements with the book, the actionable output for a future detection change.

## Risks / Trade-offs

- **Curation judgment per song.** Tonic-vs-relative-vs-transposition is a human call. → Curate
  against Chediak + the scraped arrangement, record the reasoning in a `note`/justification;
  the live print is the check. Mis-curation surfaces as a spurious hole, not a silent error.
- **Detector holes inflate the "miss" list, not regressions.** A chediak-tonal song where
  detect_key disagrees lowers the *combined* center_accuracy vs verified-only. → Report the two
  subsets separately so the `verified` 19/19 stays legible; the combined number is honest new
  signal, not a regression of an existing metric.
- **Copyright.** Only "Tom de X" + page facts — never the harmonization. → Same boundary as
  `key_baseline.GOLD`; store no chords/tables.
- **Data-gated.** Needs the book + scrapable CC charts. → Grow fact-by-fact; defer the rest;
  report coverage so it is never overstated.

## Migration Plan

Additive and reversible. New `chediak`-tonal facts only ADD to the center denominator; the
`verified` path and the four Cifra-Club metrics are byte-identical. The trava: re-run
`key_baseline.py`, diff the four Cifra-Club metrics and the `verified`-tier center value against
the pre-change baseline — must be identical. Rollback = remove the facts.

## Open Questions

- **How many Parte 4 songs overlap the existing 60-song corpus?** Only overlapping songs can be
  scored live (we scrape the corpus). Non-corpus Chediak songs can be added to the corpus first
  (a `GOLD` row) or deferred. Resolve per song at apply time.
- **Do we also want non-corpus Chediak songs as pure coverage?** They need a `GOLD` entry to be
  scraped; decide at apply whether to widen `GOLD` alongside (a small, optional extra).
- **Promote the tonal gold to the typed `corpus` package?** Deferred (D4) — revisit if a runtime
  consumer beyond the harness appears.
