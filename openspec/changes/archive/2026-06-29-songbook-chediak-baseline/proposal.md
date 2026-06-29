## Why

The validation harness still treats the **Cifra Club annotation as gold**: the four metrics
(mode, exact-tonic, relative-aware, collection) and the structural-center tier all score
`detect_key` against `cc_key` — the source's crowd-sourced "Tom:". That contradicts the
project's own Golden Rule (the Cifra Club is raw input, not truth) and has repeatedly bitten us
(Eu sei que vou te amar annotated "Em" while Chediak and a trustworthy songbook both read C
major; Coração Vagabundo's spurious "hole"). The principle the team settled on: **the tonal
*transposition* of a piece must not drive its analysis — functional harmony (degrees, functions,
cadences) is transposition-invariant, and the only legitimate arbiter is Chediak, applied to the
music itself.**

So: **the Cifra Club becomes a cifra *source* and nothing more — base of nothing.** Chediak is
the theoretical base that validates *any* cifra, and the **songbook** (62 trustworthy
arrangements, already split into `cifras/*.md`, local/gitignored) is the baseline corpus. The
center is established by Chediak's *functional* criterion (a real-tritone dominant resolving to
repose, pp.84/87) read from the music — never from an annotation. Validation measures whether our
analysis applies Chediak's theory correctly, independent of which key the arrangement sits in.

## What Changes

- **Retire the `cc_key`-anchored metrics.** Remove mode / exact-tonic / relative-aware /
  collection scored against the Cifra Club annotation, and the `cc_key`-anchored center tier
  (the `chediak-tonal-center-gold` tonal tier and `verify_tonal_center`'s "check against a given
  `cc_key`" usage). `cc_key` stops being gold for anything. **BREAKING** (the historical baseline
  numbers vs CC are intentionally dropped).
- **Establish the center by Chediak's functional criterion, from the music.** Generalize
  `verify_tonal_center` from *"does a functional dominant resolve to this given `cc_key`?"* to
  *"find the chord a functional dominant (real tritone V7/SubV7, structural/final) resolves
  to"* — the Chediak-functional tonic, with **no annotation input**.
- **New baseline over the songbook, grounded in Chediak.** Run analysis on the songbook cifras
  (locally, via `cifra_from_text` — never scraping). Report: (a) **functional-center agreement** —
  does `detect_key` match the Chediak-functional center, over the subset where the criterion
  fires (the rest quarantined, coverage reported); (b) **Chediak functional invariants** per song
  — a real tritone is classified as a dominant by its target (primary/secondary/SubV/extended,
  XVIII-XIX/XXVIII), diminished chords by type (XXI-XXII), ii-V recognized, cadences in the
  five-cadence taxonomy. All transposition-invariant.
- **Affirm transposition-invariance.** The functional reading is the product; absolute tonality
  is only a display frame and must not change degrees/functions/cadences.

## Capabilities

### New Capabilities
- `functional-analysis-baseline`: a validation baseline over a local, trustworthy songbook
  corpus that scores the analysis against **Chediak's theory** — the functional-dominant center
  criterion and the functional-classification invariants — independent of any source annotation
  and invariant to transposition.

### Modified Capabilities
- `key-accuracy-evaluation`: **remove** the Cifra-Club-`cc_key`-as-gold requirements (the four
  annotation-anchored metrics and the `cc_key`-anchored center tier). The center is no longer
  validated against an annotation; the surviving notion (functional-dominant center) moves to the
  music-grounded criterion in the new capability.

## Impact

- **New code:** a `chediak_functional_center(symbols) -> Optional[center]` (generalized
  `verify_tonal_center`) in `scripts/chediak_structural_gold.py` (or promoted into a package
  module); a songbook baseline runner (loads `cifras/*.md` via `cifra_from_text`, runs analysis,
  reports functional-center agreement + invariant checks). Tests for the generalized criterion and
  the invariant checks.
- **Modified code:** `validation/key_accuracy.py` (remove `cc_key`-anchored metrics; keep only
  what is music-grounded), `scripts/key_baseline.py` (retire or repoint away from CC; the new
  runner supersedes it), `scripts/chediak_structural_gold.py` (drop `TIER_C_TONAL` and the
  `cc_key`-checking signature; generalize the functional-center search).
- **Reuses unchanged:** the analysis engine — `detect_key`, the functional layer (functions,
  secondary/extended dominants, diminished classification, cadences), `modal_coloring`,
  `cifra_from_text`/`local-chord-input`. The engine is NOT touched beyond the functional-center
  generalization (a harness concern).
- **Does NOT touch:** the analytic core's verdicts. The change is to **validation**, not detection.
- **Corpus:** the songbook (`cifras/*.md`) is local and gitignored — only derived facts/results
  are committed, never the cifras (copyright boundary unchanged).
- **Breaking:** the four Cifra-Club metrics disappear; downstream references (ROADMAP baseline
  line, AGENTS.md state) are updated. This is intentional — those numbers measured CC-fidelity,
  which is no longer a goal.
