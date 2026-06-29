> **STATUS: REDESIGNED FOR CAMINHO 2 — ANNOTATION (2026-06-29).** The original detection
> design (Caminho 1) was invalidated by the zero-regression trava — the Chediak modal center
> is **not encoded in the Cifra Club chords** (see [PROBE-FINDINGS.md](./PROBE-FINDINGS.md)).
> This proposal now pivots to **Caminho 2**: the modal center is a **curated musicological
> fact** injected at **display time** as a cited curator note, never detected from chords.
> It is the (B) half of the analytical bifurcation whose (A) half shipped as `modal-mode-naming`.
> The detection-era specs in `specs/` still describe Caminho 1 and must be regenerated before
> implementation. See [design.md](./design.md) for the full Caminho 2 architecture.

## Why

Pieces whose true center is **modal** (Arrastão → Lá dórico, Chediak Vol. I p. 125; Procissão
→ Dó mixolídio, p. 126) read on the **tonal axis** for every mechanism we have — K-S, the CC
annotation, the 3b quality gate — because a modal piece lacks a functional dominant *by
construction*. The probe proved the finalis is **unrecoverable from the chords** (Arrastão
ends on `D7+`; Lá only ties for 2nd; Procissão's Dó appears 1×/80). So there is nothing to
*detect*.

But there **is** something to *show*: Chediak's reading is a documented fact. Displaying it as
a cited curator note, beside the algorithmic tonal reading, turns a data wall into a teaching
feature — the user sees that the Cifra Club arrangement and the composer's conception diverge,
which is a music lesson in itself. This is the **(B)** half of the bifurcation; **(A)**
(`modal-mode-naming`) already names the mode the algorithm *can* detect ("D mixolídio"). The
unlock: annotation needs only a **curated fact corpus** (cheap, copyright-safe), not a melodic
substrate (the legal/technical quagmire that doomed detection).

## What Changes

- Add a **curated modal-center annotation** rendered at display time: a cited curator note
  ("Chediak p.125: Lá dórico — a cifra está adaptada…") shown beside the tonal reading, keyed
  by song identity (artist + title), **only** for pieces whose center genuinely diverges. No
  chords are read for a verdict; nothing is detected.
- Establish a **single curated source of truth** by promoting the inert `TIER_A_CHEDIAK` facts
  (Arrastão, Procissão) into a curated dataset (Python module recommended; one copy), extended
  with a transposition-safe `finalis_from_tonal` interval. Facts only — no chords, no book text.
- **Scope = center divergence only** (offset ≠ 0). Mode-name-only divergences (Upa Neguinho,
  Pra Não Dizer — center already correct) stay with part (A); they are excluded from the
  curated set.
- **Transposition honesty:** the curated offset is read from Chediak's analysis onto the
  scraped chords (anchored to the detected tonal center), never `chediak_pc − cc_key_pc`. The
  display labels Chediak's reading as the book's, with the arrangement divergence stated.
- Replace the meaningless detection-accuracy metric with a **coverage + divergence ledger** in
  `validation/key_accuracy.py` and the baseline report (nothing is detected, so no accuracy).
- **Guardrail (inviolable):** `detect_key` and every tonal metric are untouched; the curated
  songs are already quarantined out of `center_accuracy` and the four Cifra-Club metrics. Zero
  regression by construction, proven by re-running the baseline and diffing.

## Capabilities

### New Capabilities
- `modal-center-arbitration`: the curated, display-time annotation of a piece's modal center
  (finalis + church mode) as a cited musicological fact, distinct from and additive to the
  tonal reading, keyed by song identity, never derived from the chords and never re-centering
  the analysis.

### Modified Capabilities
- `key-accuracy-evaluation`: add a degree-relative modal-center **coverage + divergence ledger**
  (not an accuracy) over the curated set, transposition-safe via the curated interval; the four
  Cifra-Club metrics and the tonal `center_accuracy` remain byte-identical.

## Impact

- **New data:** a single curated modal-center dataset (promote `TIER_A_CHEDIAK`), with the
  `finalis_from_tonal` interval + page + divergence note.
- **New code:** a presentation-layer lookup/render (curator note) mirroring `modal-mode-naming`;
  tests for identity-key matching, render presence/absence, and the divergence ledger.
- **Modified code:** `presentation/reports/markdown.py` + `html.py` (curator note block);
  `validation/key_accuracy.py` (coverage + ledger); `scripts/key_baseline.py` (report the line);
  `scripts/chediak_structural_gold.py` (point the facts at the single source).
- **Reuses unchanged:** `cifra_core/slug.py` (identity key), `labels.py` (`church_mode_pt`).
- **Does NOT touch:** `detect_key`, `detect_coloring`, `modal.py`, `segment_keys`, `TIE_BAND`,
  functions, cadences, or any tonal metric. `domain/modal_center.py` from Caminho 1 is not built.
- **Risk gate:** zero regression of the four Cifra-Club metrics and the tonal `center_accuracy`
  is inviolable, proven live against the baseline.
