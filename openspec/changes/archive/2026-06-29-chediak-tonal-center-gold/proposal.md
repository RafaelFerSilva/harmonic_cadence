## Why

The tonal `center_accuracy` metric runs over only the **19** songs whose center is verified by
a functional dominant resolving to the Cifra Club key (`verified` tier). The other ~41 corpus
songs are quarantined (`unverified`) — not because their center is wrong, but because no
*mechanical* criterion confirms it. Chediak's Parte 4 analyzes ~80 MPB songs, each headed
**"Tom de X maior/menor"** — an independent, cited tonal-center fact. Harvesting those labels
gives a **non-circular** center anchor that does not depend on a dominant, expanding center
coverage well past 19 and — more valuably — **surfacing detector holes** where `detect_key`
disagrees with the book's tonal center (a real bug signal today hidden by quarantine).

This is the productive use of Parte 4 discovered while trying to grow the modal corpus
(`grow-modal-center-corpus`, parked — Parte 4 is tonal, not modal). It strengthens the *tonal*
center gold, the tier the modal corpus could not.

## What Changes

- Harvest Chediak Vol. I Parte 4 **"Tom de X maior/menor"** labels (II.A major pp.189-244,
  II.B minor pp.250-282, and the exercises C pp.295-317 with answers D pp.321-332) as
  **cited tonal-center facts** with provenance `chediak` and `center_type = tonal`. Each fact
  is `(artist, song, chediak_tom, structural_offset, page)` — **facts only**, never the book's
  harmonizations/chord tables/sheets (copyright wall).
- Extend the structural-center gold so the **`chediak` tier carries tonal centers too** (today
  it only feeds the modal ledger). A `chediak`-tonal fact feeds the **degree-relative tonal
  `center_accuracy`** (the same offset metric as the `verified` tier); `center_accuracy` runs
  over `verified` ∪ `chediak-tonal`, with the `chediak`-tonal subset size reported so coverage
  is visible.
- **CRUX — the offset is curated degree-relative, never absolute subtraction.** A
  `chediak`-tonal fact's `structural_offset` is the degree relationship between Chediak's tonic
  and the Cifra Club annotation (tonic confirmed → 0; CC annotated the relative → ±3; another
  degree → its offset), curated by reading Chediak against the scraped arrangement — NOT
  `chediak_tom_pc − cc_key_pc` (Chediak's edition and the CC arrangement may be transposed, the
  Pra-Não-Dizer Mi-vs-Fá trap). Transposition-invariant by construction.
- Report a per-song **center hole** for `chediak`-tonal songs where `detect_key` disagrees with
  the cited center (the bug-surfacing payload).

## Capabilities

### New Capabilities
<!-- none — extends an existing capability with data + a tier semantics refinement -->

### Modified Capabilities
- `key-accuracy-evaluation`: the `chediak` provenance tier may carry **tonal** centers (not only
  modal), which feed the degree-relative tonal `center_accuracy` over `verified` ∪
  `chediak-tonal`; the `chediak`-tonal offset is a curated degree fact, not absolute
  subtraction; coverage and the per-song center hole are reported. The four Cifra-Club metrics
  and the existing `verified`-tier `center_accuracy` value remain unchanged.

## Impact

- **New data:** `chediak`-tonal facts in `scripts/chediak_structural_gold.py` (or the structural
  map the baseline builds) — `(artist, song, chediak_tom, structural_offset, page)`, curated
  degree-relative.
- **Modified code:** `validation/key_accuracy.py` (`evaluate_corpus` runs `center_accuracy` over
  `verified` ∪ `chediak-tonal`; report the `chediak`-tonal subset size + hole) and
  `scripts/key_baseline.py` (build the `chediak`-tonal structural map; print coverage + hole).
- **Reuses unchanged:** `center_ok` (already degree-relative offset), `evaluate_song`/`KeyEval`
  (`structural_offset` plumbing already exists), `verify_tonal_center` (the `verified` tier is
  untouched).
- **Does NOT touch:** `detect_key`, `detect_coloring`, the modal `CORPUS`/ledger, the four
  Cifra-Club metrics, or the `verified`-tier `center_accuracy` value.
- **Risk gate:** zero regression of the four Cifra-Club metrics and the current `verified`-tier
  `center_accuracy` (19/19), proven live against the baseline. New `chediak`-tonal songs only
  ADD to the center denominator; they never alter the existing numbers.
- **Constraint:** requires Chediak Vol. I (`base_estudo/`, gitignored) for the "Tom de X" labels
  + pages, and network to scrape each song; each fact's offset is curated per song (judgment:
  tonic vs relative vs transposition), so the corpus grows fact-by-fact, never by guessing.
