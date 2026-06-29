# Tasks — chediak-tonal-center-gold

> Harvest Chediak Parte 4 "Tom de X maior/menor" labels as cited `chediak`-tonal center facts,
> feeding the existing degree-relative `center_accuracy` over `verified` ∪ `chediak-tonal`.
> Data + small harness change; does NOT touch `detect_key`. Data-gated: needs Chediak Vol. I
> (`base_estudo/`, gitignored) + network. The offset is curated degree-relative (design D2),
> never absolute subtraction.

## 1. Baseline trava (zero-regression reference)

- [x] 1.1 Baseline reference (ran live this session): **modo 86 · exata 76 · relativa 83 · coleção 97 · centro TONAL verificado 100% (19/19) · modulantes 100%**, modal ledger n=2.

## 2. Harvest the "Tom de X" facts (facts only, copyright wall)

- [x] 2.1 Read the work-index (pp.354-355) + each analyzed corpus song's header. 8 corpus songs are in Parte 4; harvested toms for 7 (Triste's tom lives in the exercise answers, unread). (HARVEST.md)
- [x] 2.2 Matches listed `(artist, song, chediak_tom, page)`; the ~50 non-analyzed corpus songs have no fact (deferred — none to add). Non-corpus Chediak songs left for a later `GOLD` widening.

## 3. Curate the degree-relative offset per song (the crux, design D2/D3)

- [x] 3.1 Curated 5 facts degree-relative from (Chediak tom, cc_key role): Papel Marché/Cor. Estudante/Trocando = offset 0 (same role); Valsinha = 0 (Am vs Cm = transposition of the same minor tonic, NOT Am−Cm); Coração Vagabundo = 9 (cc_key Eb is the relative MAJOR of Chediak's Cm). Never `chediak_tom_pc − cc_key_pc`. (HARVEST.md)
- [x] 3.2 Deferred Eu sei que vou te amar (Em vs C ambiguous), Atrás da Porta (E vs Bm ambiguous), Triste (answer unread) — not guessed.

## 4. Commit the facts + tier semantics

- [x] 4.1 Added `TIER_C_TONAL` to `scripts/chediak_structural_gold.py` — 5 facts `(artist, song, chediak_tom, structural_offset, page, justification)` + `chediak_tonal_offset()` lookup. Facts only.
- [x] 4.2 `scripts/key_baseline.py`: chediak-tonal entries added ONLY for non-verified songs (verified-19 untouched, no double-count), provenance `chediak`, curated offset.

## 5. Harness: center_accuracy over verified ∪ chediak-tonal (design D1/D5)

- [x] 5.1 `evaluate_corpus`: `provenance` on `KeyEval`; `center_accuracy` over `verified` ∪ `chediak`-tonal; reports `verified_n`/`verified_center_accuracy` and `chediak_tonal_n`/`chediak_center_accuracy` separately (never blended).
- [x] 5.2 `chediak`-modal still routed to the ledger; `unverified` quarantined. Four CC metrics + verified-tier value byte-identical (proven in 7.1).
- [x] 5.3 Added 4 tests to `test_key_accuracy.py`: chediak-tonal counts separately; offset is curated not absolute subtraction (Valsinha Am-vs-Cm → 0, not 9); disagreement → miss/hole; adding chediak-tonal never changes the verified value.

## 6. Baseline reporting + the center hole (design D5)

- [x] 6.1 `scripts/key_baseline.py`: separate verified + chediak-tonal blocks, each with n, accuracy, and the per-song hole (cc_key, offset, detected).

## 7. Zero-regression trava + docs + specs

- [x] 7.1 Ran live: **modo 86 · exata 76 · relativa 83 · coleção 97 · verified center 100% (19/19) · modulantes 100% — IDENTICAL to task 1.1 (zero regression).** New `chediak`-tonal tier n=3, 2/3 (the other 2 of the 5 facts are already verified → corroborated, no double-count). **Hole surfaced: Coração Vagabundo — detector reads Eb maior (the relative), Chediak's center is Dó menor (offset 9).**
- [x] 7.2 `make test` green (395); `make lint` clean. (validate below)
- [ ] 7.3 Update `ROADMAP.md`/`AGENTS.md`: note the `chediak`-tonal center tier, the new coverage, and the Coração Vagabundo detector hole (future detection work). Then `openspec archive`.
