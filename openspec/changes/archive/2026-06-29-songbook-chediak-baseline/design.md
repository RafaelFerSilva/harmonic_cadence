## Context

The harness today scores `detect_key` against `cc_key` (the Cifra Club "Tom:") across four
metrics, plus a `cc_key`-anchored center tier ([key_accuracy.py](packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py),
[key_baseline.py](scripts/key_baseline.py), [chediak_structural_gold.py](scripts/chediak_structural_gold.py)).
`verify_tonal_center(symbols, cc_key_pc)` already encodes Chediak's functional criterion
(pp.84/87 — a real-tritone V7/SubV7 resolving to a chord in structural/final position makes that
chord the tonic) but is wired to *confirm a given `cc_key`*. The team's decision: the Cifra Club
is a cifra **source only**; Chediak is the validation base; the **songbook** (`cifras/*.md`,
local/gitignored) is the corpus. Functional harmony is **transposition-invariant** — the absolute
key is a display frame, not an input to the analysis.

## Goals / Non-Goals

**Goals:**
- Validate the analysis against **Chediak's theory applied to the music**, never against a source
  annotation; invariant to transposition.
- Establish the tonal center by Chediak's functional-dominant criterion read **from the chords**,
  with no `cc_key`.
- Baseline over the songbook locally (`cifra_from_text`), never scraping.
- Retire the `cc_key`-anchored metrics and tier cleanly.

**Non-Goals:**
- Touching the analytic core's verdicts (`detect_key`, functions, travas, `modal_coloring`).
  The only engine-adjacent change is generalizing the functional-center *search* (a harness tool).
- A per-song *key* gold curated by hand (that reintroduces an annotation). The gold is the
  functional rule, applied live.
- Committing songbook cifras (copyright boundary; only derived results are committed).

## Decisions

### D1 — Generalize `verify_tonal_center` → `chediak_functional_center(symbols)`

Turn the confirm-against-`cc_key` check into a **search**: scan the progression for a real-tritone
dominant (`Category.DOMINANT`: V7 or SubV7) resolving by bass to a repose chord in a
structural/final window, and **return that target pc + its chord quality (major/minor) as the
Chediak-functional center** — or `None` if no such resolution exists. This is the same rule
(pp.84/87), now *finding* the tonic instead of validating a guess. No annotation enters.

*Why over alternatives*: K-S/`detect_key` is the system under test, so it cannot be its own gold.
The functional-dominant rule is an **independent, principled** gold (Chediak's repose criterion),
mechanically distinct from K-S — so agreement is meaningful, not circular.

### D2 — Center is CORROBORATION, not a detector accuracy (revised during apply)

Implementation revealed that an annotation-free functional center is **not a reliable gold**:
identifying *which* repose is the tonic without an annotation is exactly the hard MIR problem
`detect_key` already tackles, so `chediak_functional_center` is just a *second heuristic* (bossa
tunes routinely open on a non-tonic — Dindi on `A7M`, etc.). Comparing two heuristics yields
ambiguous disagreement, not a precision metric.

So the center is reported as **corroboration**, not "detect_key accuracy": `chediak_functional_center`
(conservative — anchored on the structural repose, confirmed by a functional dominant; quarantine
when not confirmed) is run beside `detect_key`. Where the two **independent** methods **agree**, it
is a high-confidence center; where they **disagree**, the song goes on a **curation worklist** (a
human/Chediak citation adjudicates) — NOT scored as a detector miss. Coverage (fired / total) and
the agree/disagree split are reported honestly; no number claims detector accuracy.

*Why*: it would be dishonest to score `detect_key` against a gold that is itself an unreliable
heuristic. Corroboration is the truthful framing — and the disagreement list is genuinely useful
(it is the shortlist of songs worth a Chediak look).

### D3 — Chediak functional invariants (transposition-invariant, per song)

Independent of the center, check that the functional reading obeys Chediak — the rules already
implemented across 39 archived changes, now asserted as baseline invariants:
- A **real tritone** (`Category.DOMINANT`) is read as a dominant classified by its **target**:
  primary `V7→I`, secondary `V7/x`, `SubV7`, auxiliary `Daux`, extended `Dext` (XVIII-XIX, XXVIII).
- **Diminished** chords classified by type (ascending/descending/auxiliary, XXI-XXII), `vii°7` as
  dominant (`dim7-as-dominant`, p.90) — never mislabeled `Emp`.
- **ii-V** recognized (the `D2` cadencial, XIX); **cadences** tagged within the five-cadence
  taxonomy (XXXII).
These hold in any transposition (they are degree/quality-relative). The baseline reports
violations as functional-analysis defects — the real quality signal, replacing CC-fidelity.

*Open*: the exact invariant set to assert first vs. grow incrementally — start with the
center + the dominant-classification + cadence-presence checks; expand per song as holes surface.

### D4 — Corpus loader: the songbook, locally

The baseline loads `cifras/*.md`, extracts the chord lines, and ingests via `cifra_from_text`
(the `local-chord-input` path) — **no scraping, no `cc_key`**. Each file yields a `Cifra`
(`key=""`); the runner feeds `AnalysisService.analyze_song_data_structured` and the
functional-center search. The songbook stays gitignored; only the aggregate results/holes are
committed (as a baseline report doc, never the cifras).

*Open*: a few songbook entries modulate; the functional-center search returns the **home/final**
resolution. Multi-region songs can be deferred to the existing `dominant_regions` machinery later;
v1 scores the single structural cadence.

### D5 — Clean retirement of the `cc_key` gold

Remove from `key_accuracy.py`: `parse_key`-vs-`cc_key` scoring for mode/exact/relative/collection
and the `center_ok(detected, cc_key, offset)` tier; remove `TIER_C_TONAL` and the
`cc_key`-checking arm of `verify_tonal_center` from `chediak_structural_gold.py`. `key_baseline.py`
(the CC corpus runner) is superseded by the songbook runner; keep it only if a CC scrape is still
wanted as a *demo of the source adapter*, explicitly NOT a validation gold. The four-metric numbers
leave the ROADMAP/AGENTS baseline line, replaced by the functional-center coverage + invariant
results.

*Why a clean break*: keeping the `cc_key` metrics "for reference" would re-anchor the project on
the annotation the team just demoted; a half-measure invites backsliding.

## Risks / Trade-offs

- **Loss of the historical baseline numbers.** The 86/76/83/97 line disappears. → Intentional;
  those measured CC-fidelity. The new numbers (functional-center coverage/agreement, invariant
  pass-rate) measure what we actually care about. Document the transition.
- **Coverage shrinks to where the dominant rule fires.** Modal/static bossa (Donato) won't get a
  center gold. → Honest by design (quarantine + coverage); the invariants (D3) still cover them.
- **Possible circularity worry** (detect_key uses cadential cues; so does the functional center).
  → The functional center is the *pure* dominant-resolution rule; `detect_key` is K-S-led with
  heuristic tie-breaks. Distinct mechanisms → agreement is informative. Where they share a cue and
  always agree, that is a *true* easy case, not a rigged one.
- **Songbook is one genre (bossa).** → Fine for v1; the corpus is swappable (any `cifras/*.md`),
  and the gold is the rule, not the corpus.

## Migration Plan

1. Add `chediak_functional_center` (generalize) + tests. 2. Add the songbook baseline runner +
the invariant checks. 3. Remove the `cc_key`-anchored metrics/tier. 4. Run the new baseline live
over `cifras/*.md`; record coverage + holes. 5. Update ROADMAP/AGENTS to the new baseline.
Rollback = restore the removed harness code (the engine never changed).

## Open Questions

- Which invariants to assert in v1 vs grow later (D3)?
- Keep `key_baseline.py` as a CC-source *demo* (clearly non-gold) or delete it (D5)?
- Modulating songbook tunes: single structural cadence now, `dominant_regions` later (D4)?
