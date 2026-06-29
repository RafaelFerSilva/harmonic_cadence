## Context

`modal-center-arbitration` shipped the curated modal-center machinery (typed corpus with
mandatory citation, slug identity lookup, curator note in MD/HTML/JSON, coverage + divergence
ledger) seeded with **n=2** facts. Every consumer (`lookup_modal_center`, the three renders,
`modal_center_ledger`, the baseline block) iterates `CORPUS`, so growth needs **no code
change** — only vetted data. The constraint is provenance, not engineering: each fact is a
musicological claim that must be sourced from Chediak Vol. I and verified against the live
Cifra Club arrangement, under the project's Golden Rule (the chords are raw input; the truth
is Chediak + the algorithm, never the CC annotation).

The honest blocker recorded in `PROBE-FINDINGS.md`: Chediak's modal center is **unrecoverable
from the chords** (Arrastão ends on `D7+`, Lá only ties; Procissão's Dó is 1×/80). That is
exactly why these are *curated annotations*, not detections — and why each new fact needs a
human reading Chediak, not a heuristic.

## Goals / Non-Goals

**Goals:**
- Raise modal-center coverage beyond n=2 with additional **genuine center-divergence** facts
  from Chediak Vol. I, each cited to a page.
- Codify the **admission protocol** (the spec's ADDED requirement) so the corpus stays
  trustworthy as it grows and the inviolable tonal baseline never moves.
- Keep the corpus the single source (`TIER_A_CHEDIAK` already reads from it).

**Non-Goals:**
- Any change to detection, the renders, the ledger, or the metrics — pure data.
- Mode-name-only divergences (center already correct, `finalis_from_tonal == 0`) — those are
  part (A)'s job and are explicitly rejected from this corpus.
- A melodic/MIDI corpus or any attempt to *detect* the finalis (Caminho 1, still data-blocked).
- A coverage target/quota — facts accrue as a musician curates them; n grows honestly.

## Decisions

### D1 — Candidate sourcing: Chediak's modal section first, then cross-references

Mine candidates from Chediak Vol. I Parte 2 (the modal pages ~121-127) and any modal analysis
cited elsewhere in the volume. For each candidate, classify with the part-(A)/part-(B)
partition: only **center divergence** (`finalis_from_tonal != 0`) enters here. The four
already-probed `chediak`-tier songs are settled — Arrastão & Procissão are in; Upa Neguinho &
Pra Não Dizer are mode-name-only (rejected). New candidates come from the rest of the modal
repertoire Chediak names.

*Why over alternatives*: scanning the whole book for any modal mention would surface
mode-name-only and tonal pieces that waste curation; starting from the dedicated modal section
maximizes the hit rate of genuine center divergence.

### D2 — `finalis_from_tonal` curated live, per fact (the crux, unchanged from parent D5)

For each admitted song: scrape chords → `detect_key` → take the detected tonal center as the
anchor → read Chediak's finalis as an interval **above that anchor** in the arrangement's pitch
space. Record it as `finalis_from_tonal` (0..11, non-zero). Never `chediak_pc − cc_key_pc`.
The live baseline ledger already prints `(eixo tonal, Chediak, finalis +N, p.N)` per fact —
use it as the curation worksheet and sanity check (as it confirmed +7 / +3 for the seed pair).

### D3 — Data-gated apply; the fact list is produced at implementation time

This proposal commits the **protocol and the slots**, not a pre-baked fact table: producing
correct facts requires the book (`base_estudo/`, gitignored) open to the cited page and network
to scrape each candidate. The apply phase curates fact-by-fact, each gated by D2 + the spec's
admission protocol. If a session can only verify k of m candidates (404s, ambiguous transposes),
it commits k and defers the rest — coverage is never overstated.

*Why*: pre-baking facts without the live check would risk shipping a wrong interval or page —
the exact "fudged gold" the project forbids.

### D4 — Tests grow for free; add identity assertions per fact

`test_modal_centers_corpus.py` parametrizes over `CORPUS`, so the citation/range/non-zero
invariants cover new facts automatically. Add one explicit identity-resolution assertion per
new song (artist/title slug variants resolve) so a future rename can't silently break the
lookup.

## Risks / Trade-offs

- **Thin yield.** Chediak's genuinely center-divergent MPB set may be small; some candidates
  will be mode-name-only or tonal. → Accept; commit what verifies, defer the rest, report
  coverage honestly (the ledger already does).
- **Arrangement drift.** `finalis_from_tonal` is curated against today's scraped chords; if CC
  re-arranges a song, the interval can rot. → Flag the dependency in each fact's `note`
  (as the seed facts do); the live baseline re-derivation catches drift.
- **Identity brittleness.** Title/artist variants must slug-match the scrape. → Per-fact
  identity test (D4); a miss degrades to "no note" (safe), never a wrong note.
- **Provenance discipline.** Only facts (center/mode/interval/page/note) — never book text,
  tables, or chords. → Same boundary as the seed corpus and `key_baseline.GOLD`.

## Migration Plan

Additive and reversible: each fact is one `ModalCenterFact` literal. Rollback = remove the
entry. No schema change, no detection change, no metric change. The post-add baseline diff is
the gate; if any of the four CC metrics or the tonal `center_accuracy` move, the fact is
reverted and investigated (it would mean the machinery, not the data, regressed).

## Open Questions

- **How many candidates exist?** Resolved only by reading Chediak's modal section at apply time
  (D3). The change succeeds at any n ≥ 3 (strictly more than the seed); it does not need a
  fixed target.
- **Do any candidates need a new church mode beyond the `Literal[ChurchMode]` set?** All six
  modes are already typed; a candidate in lydian/locrian (rare in MPB) would be the first user
  of those literals — allowed, no code change.
