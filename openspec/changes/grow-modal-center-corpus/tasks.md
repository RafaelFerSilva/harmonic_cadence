# Tasks — grow-modal-center-corpus

> **STATUS: PARKED (2026-06-29) — data-gated at n=2.** Apply ran the admission protocol live
> and found Chediak's named modal pieces with a scrapable Cifra Club chord chart are exhausted:
> the modal-example section (§XXXVI.4) yields only Gravidade as a possible new center divergence.
> Parte 4 (user-requested) is **tonal** ("Tom de X maior/menor" per song), so it cannot grow the
> modal corpus. Re-scoped to a tonal-center harvest in a separate change (`chediak-tonal-center-gold`).
> The machinery from `modal-center-arbitration` is correct and untouched.
> **UPDATE (2026-06-29):** Gravidade was later analyzed with a trustworthy chord chart (via the new
> `local-chord-input`) and found to be **mode-name-only** (center = Si, offset 0), NOT a divergence —
> so Vol. I §XXXVI.4 is **definitively exhausted at n=2**. Reaching n≥3 needs a NEW cited authority
> (Chediak Vol. II / literature), not more chords. See [APPLY-FINDINGS.md](./APPLY-FINDINGS.md).

> Pure curation/data front. Reuses all `modal-center-arbitration` machinery — no detection,
> render, ledger, or metric code changes. Each new fact is gated by the admission protocol
> (spec) + the live `finalis_from_tonal` curation (design D2). Data-gated: needs Chediak
> Vol. I (`base_estudo/`, gitignored) + network to scrape candidates.

## 1. Baseline trava (record the zero-regression reference)

- [x] 1.1 Ran `uv run python scripts/key_baseline.py` — reference: **modo 86 · exata 76 · relativa 83 · coleção 97 · centro tonal 100% (19/19) · modulantes 100%**, modal coverage n=2. (APPLY-FINDINGS.md)

## 2. Candidate discovery (Chediak Vol. I, Parte 2 modal section)

- [x] 2.1 Read Chediak Vol. I pp.125-127 (§XXXVI.4, the canonical modal-example set; PDF offset = printed+1). The 6 examples: Cravo e Canela (iônico), Arrastão (dórico), Upa Neguinho + Procissão (mixolídio), Pra não dizer (eólio), Gravidade (lídio b7).
- [x] 2.2 Partitioned (design D1): Arrastão/Procissão **already in corpus**; Upa Neguinho/Pra-Não-Dizer **mode-name-only → reject** (part A); Cravo e Canela **tonal (ionian = major, offset 0) → reject**; **Gravidade (C lídio b7, p.127) = the only genuine new center-divergence candidate**.

## 3. Per-candidate live verification (the admission protocol)

- [~] 3.1 **BLOCKED BY DATA — deferred, not guessed.** Gravidade has **no chord chart on Cifra Club** (lyrics-only `/caetano-veloso/565091/letra/`; song-slug URL redirects to artist) → `EmptyCifra`. Cravo e Canela slug also unresolved (and tonal anyway). No candidate resolves to a scrapable substrate. (APPLY-FINDINGS.md)
- [~] 3.2 N/A — no scrapable candidate reached this step.
- [~] 3.3 N/A — cannot curate `finalis_from_tonal` without scraped chords (design D2 requires reading Chediak's analysis ONTO the scraped chords).
- [~] 3.4 **Parte 4 checked (user request) — it is TONAL, not modal.** Every analyzed song is headed "Tom de X maior/menor" (e.g. PALCO = Mi maior). Parte 4 has no modal section; it cannot grow `modal_centers` (a Parte 4 center is the tonal tonic = offset 0, or a detector miss = a tonal bug). It CAN feed the separate tonal structural-center `chediak` gold — a different change. (APPLY-FINDINGS.md)

## 4. Commit the facts (single source)

- [ ] 4.1 Add each verified `ModalCenterFact` to `harmonic_analysis.corpus.modal_centers.CORPUS` with a mandatory `Citation` (source/volume/page). Facts only — no chords, no book text. Commit only what verified this session; defer the rest.
- [ ] 4.2 Confirm `TIER_A_CHEDIAK` (which reads from `CORPUS`) reflects the new center-divergence facts automatically (no duplicate copy).

## 5. Tests

- [ ] 5.1 Extend `tests/test_modal_centers_corpus.py`: the parametrized citation/range/non-zero invariants cover new facts automatically — add one identity-resolution assertion per new song (slug variants resolve; unknown misses).
- [ ] 5.2 `make test` green; `make lint` clean.

## 6. Zero-regression trava + docs

- [ ] 6.1 Re-run `uv run python scripts/key_baseline.py` live; **diff** the four Cifra-Club metrics and the tonal `center_accuracy` against task 1.1 — must be IDENTICAL. Confirm the modal-center ledger now shows the higher coverage (n>2) with each new fact's `(eixo tonal, Chediak, finalis +N, p.N)`.
- [ ] 6.2 Update `ROADMAP.md`/`AGENTS.md`: bump the curated modal-center coverage count and note zero tonal regression. `openspec validate grow-modal-center-corpus --strict` passes. Then `openspec archive`.
