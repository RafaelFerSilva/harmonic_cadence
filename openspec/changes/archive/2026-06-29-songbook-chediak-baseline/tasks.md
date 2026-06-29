# Tasks — songbook-chediak-baseline

> Reframe the VALIDATION harness: Cifra Club = cifra source only; Chediak = validation base;
> the local songbook (`cifras/*.md`, gitignored) = corpus. Retire the cc_key-anchored metrics;
> the center is established by Chediak's functional-dominant criterion read from the music.
> Does NOT touch the analytic core (detect_key, travas, modal_coloring) beyond generalizing the
> functional-center search. Functional analysis is transposition-invariant.

## 1. Reference snapshot (before the break)

- [x] 1.1 Record the current cc_key-anchored baseline numbers verbatim (modo/exata/relativa/coleção + verified center 19/19) once, as the historical line being retired — for the changelog/migration note, NOT as a future gold.

## 2. Chediak-functional center (find the tonic from the music)

- [x] 2.1 Add `chediak_functional_center(symbols) -> Optional[(pc, mode)]`: generalize `verify_tonal_center` from "confirm a given cc_key" to **search** for a real-tritone V7/SubV7 resolving by bass to a structural/final repose chord; return that chord's pc + quality, or None. No annotation input. (Reuse the existing tritone/`Category.DOMINANT` + bass-target logic.)
- [x] 2.2 Unit tests: a clear ii-V-i / V-I yields the resolved tonic + mode; a static modal vamp yields None; transposing the progression maps the center by the same interval (invariance).

## 3. Songbook corpus loader (local, no scraping)

- [x] 3.1 A loader that reads `cifras/*.md`, extracts chord lines, and ingests via `cifra_from_text` → a `Cifra` (`key=""`). No network, no cc_key. Skip files with no valid chords (report them).
- [x] 3.2 Make the corpus path configurable (default `cifras/`) so the gold is the rule, not the specific corpus.

## 4. Functional-center metric + invariants (the new baseline)

- [x] 4.1 For each songbook cifra: run `detect_key` and `chediak_functional_center`; where the latter fires, score agreement (pc + mode). Quarantine the rest; report coverage (n fired / n total). List the per-song functional-center **hole** (detected vs functional center).
- [x] 4.2 Assert the Chediak functional invariants per song (start: real-tritone → dominant-by-target; diminished-by-type / vii°7→dominant; ii-V recognized; cadence in the 5-cadence taxonomy). Report violations as functional defects. (Grow the invariant set incrementally.)
- [x] 4.3 Tests: agreement counted; quarantine counted, not scored as a miss; a fabricated transposition does not change any verdict; an invariant violation is reported.

## 5. Retire the cc_key gold

- [x] 5.1 Remove from `validation/key_accuracy.py` the cc_key-anchored scoring (mode/exact/relative/collection vs `cc_key`) and the `center_ok(detected, cc_key, offset)` tier + its plumbing (`structural_offset`/`provenance` as cc_key gold). Keep only music-grounded code.
- [x] 5.2 Remove `TIER_C_TONAL` and the cc_key-checking arm of `verify_tonal_center` from `scripts/chediak_structural_gold.py` (the functional-center search in 2.1 supersedes it).
- [x] 5.3 Replace `scripts/key_baseline.py` with the songbook runner (or repoint it). If a CC scrape is kept, label it explicitly a **source-adapter demo**, never a validation gold.
- [x] 5.4 Update tests that asserted the cc_key metrics (`test_key_accuracy.py`, `test_modal_center_ledger.py` if affected) to the new music-grounded surface; remove obsolete cc_key-gold tests.

## 6. Run, document, archive

- [x] 6.1 Run the new baseline live over `cifras/*.md`; record functional-center coverage + agreement + holes, and the invariant pass-rate. This is the new zero-regression reference.
- [x] 6.2 `make test` green; `make lint` clean; `openspec validate songbook-chediak-baseline --strict` passes.
- [x] 6.3 Update `ROADMAP.md`/`AGENTS.md`: the new principle (Cifra Club = source only; Chediak = validation base; songbook = corpus), the retired four-metric line, and the new functional baseline numbers. Then `openspec archive`.
