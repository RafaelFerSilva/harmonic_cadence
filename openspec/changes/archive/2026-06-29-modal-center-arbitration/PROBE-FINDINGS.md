# Probe findings — why `modal-center-arbitration` is blocked by data

**Date:** 2026-06-28. **Method:** before writing any code, ran the zero-regression trava —
`scripts/key_baseline.py` (baseline reference) + a live probe of the four `chediak`-tier
modal facts in `scripts/chediak_structural_gold.py::TIER_A_CHEDIAK`, inspecting
`detect_key`, `modal._central_pc` (finalis), `modal.detect_mode`, and
`verify_tonal_center` against the real Cifra Club chords.

## Baseline (unchanged reference)

`modo 86% · exata 69% · relativa 76% · coleção 97% · centro TONAL 79% (15/19) ·
modulantes 100%`.

## The four modal facts vs. live data

| Song | Chediak center | cc_key (live) | `detect_key` | finalis `_central_pc` | Finding |
|---|---|---|---|---|---|
| Arrastão | A dorian (p125) | **G** | D major | **E** (bass E×11, A×8, D×8; ends `D7+`) | A center **unrecoverable** — no cadence to A, A only tied-2nd |
| Procissão | C mixolydian (p126) | D | A major | D | **C appears 1× in 80 chords** — piece oscillates D/A; C impossible |
| Upa Neguinho | D mixolydian (p126) | B (transposed) | D major | **D ✓** | center already correct; only *mode name* (mixo) diverges |
| Pra Não Dizer | E aeolian (p127) | Fm (transposed) | F minor | **F ✓** | center already correct (=cc); only *mode name* (aeolian) diverges |

Arrastão full chords (n=46): `G Em9 A7/9 E Em9 A7/9 E F#m7 B7 E G7+ A7/9 C D7+ C7+ D7+
C7+ D7+ G7 Am A7/9 B D/F# Dm/F Am/E Am/C Dm7 G7 Em9 A7/9 E Em9 A7/9 E F#m7 B7 E G7+ A7/9
D7+ C7+ D7+ D B C7+ D7+`.

## Conclusion

The design assumed a bass-centric finalis + modal cadence would recover the modal center.
The data refutes it:

1. **Arrastão → A is unrecoverable** from these chords (the flagship case fails its own
   mechanism).
2. **Procissão → C is impossible** (C essentially absent — the CC arrangement is in a
   different conception than Chediak's).
3. The two "clean" songs (Upa, Pra Não Dizer) need **no center recovery** — their center is
   already detected correctly; only the *mode name* diverges, which is `modal_coloring`'s job.
   Their cc_key annotations are themselves transposed vs. the chords (Upa B-vs-D, Pra Não
   Dizer Fm-vs-E).

Therefore the arbitration is **blocked by data, not by mechanism**: it needs a curated MPB
modal corpus whose chords encode the finalis (melody is unavailable; harmony alone does not
suffice). Building the overlay + metric as specified would ship a detector that misses
Arrastão and a metric scoring ~0% on the only genuine center-divergence cases — or force a
fudged gold, which the project ethos forbids. This confirms the ROADMAP's original
"bloqueado: exige um corpus de MPB modal curado".

**Golden Rule (codified this session in AGENTS.md / ROADMAP.md):** Cifra Club = raw input
(chords only; its annotations are not the truth and do not encode the modal center);
algorithm + Chediak = ground truth. A detection target is implementable only if the raw
data encodes it.
