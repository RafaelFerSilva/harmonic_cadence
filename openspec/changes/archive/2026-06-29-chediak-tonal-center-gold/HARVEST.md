# Harvest — Chediak Parte 4 "Tom de X" → chediak-tonal center facts

**Date:** 2026-06-29. **Method:** read the alphabetical work-index (printed pp.354-355, PDF
350-351) to map corpus songs → analysis pages, then read each song's analysis header
("Tom de X maior/menor"). PDF↔printed offset drifts (scanned book); each page verified by its
footer. Offsets curated **degree-relative** from (Chediak tom, cc_key role), NEVER absolute
subtraction, NEVER from `detect_key` (no circularity).

## Corpus songs Chediak analyzes (from the work-index)

8 of the 60 corpus songs appear in Parte 4: Eu sei que vou te amar (207), Papel Marché (227),
Coração de Estudante (232), Trocando em Miúdos (234), Valsinha (250), Coração Vagabundo (263),
Atrás da Porta (276-277), Triste (312, exercise).

## Curated facts (committed this batch)

| Song | Chediak tom | page | cc_key (GOLD) | curated offset | reasoning |
|---|---|---|---|---|---|
| Papel Marché | Dó maior (C) | 227 | C | **0** | same note, same role → cc_key C is the tonic (Chediak confirms non-circularly) |
| Coração de Estudante | Fá maior (F) | 232 | F | **0** | same note, same role |
| Trocando em Miúdos | Dó maior (C) | 234 | C | **0** | home tom Dó (modulates C→Cm→G→C); cc_key C confirms the home tonic |
| Valsinha | Lá menor (Am) | 250 | Cm | **0** | both name the MINOR TONIC (Am vs Cm = pure transposition) → role offset 0, NOT Am−Cm=9 |
| Coração Vagabundo | Dó menor (Cm) | 263 | Eb | **9** | Eb is the RELATIVE MAJOR of Cm → CC annotated the relative; true center 3 semitones below cc_key (offset 9 = −3), transposition-invariant |

The offset-0 facts upgrade their songs from `unverified` to `chediak`-tonal, expanding center
coverage non-circularly. Coração Vagabundo (offset 9) exercises the degree-relative machinery
beyond 0 and is a prime detector-hole probe (detect_key picking Eb = the relative → a miss).

## Deferred (admission protocol: never guess)

| Song | Chediak tom | page | cc_key | why deferred |
|---|---|---|---|---|
| Eu sei que vou te amar | Dó maior (C) | 207 | Em | cc_key Em is neither the tonic nor the relative (Am) of C major — ambiguous transposition; needs chord-level resolution |
| Atrás da Porta | Si menor (Bm) | 276 | E | cc_key E is neither Bm's tonic nor its relative (D); modulates to Si maior (parallel). Ambiguous; needs chord-level resolution |
| Triste | (exercise) | 312 | G | tom is in the answers (D, pp.321-332), not read this session; defer until cited |

These three are real candidates blocked on a transposition judgment / unread answer page —
reopen by inspecting the scraped chords (Eu sei, Atrás da Porta) or reading the answer (Triste).

## Net

5 committed `chediak`-tonal facts (4 offset-0 + 1 offset-9), 3 deferred with reasons. All 5
already scrape (they are GOLD corpus entries seen live in the baseline). Coverage grows
fact-by-fact; the remaining ~50 corpus songs Chediak does not analyze in Vol. I (no fact).

## CORREÇÃO (pós-archive, 2026-06-29) — Coração Vagabundo removido

Ao "atacar o 3d" (o suposto buraco do detector), a sonda ao vivo das CIFRAS derrubou a
curadoria do offset 9: o arranjo do Cifra Club de **Coração Vagabundo começa em Eb e TERMINA
em Eb7M/G, sem nenhum acorde Cm** — repousa em **Mi♭ MAIOR**, não na relativa menor de Chediak.
O detector está **certo** para este arranjo; a concepção "Dó menor" de Chediak é de outro
arranjo que estas cifras **não codificam** (a Regra de Ouro de novo).

Logo o fato offset-9 era **mis-curado** (inferi "Eb = relativa de Cm" sem confirmar o centro
real do arranjo, que o protocolo D3 exigia). **Removido** de `TIER_C_TONAL`. O tier fica n=4,
todos offset 0 (2 ativos, 100%, sem buraco). O 3d foi invalidado no ROADMAP.

**Lição:** para offset ≠ 0, confirmar o centro REAL do arranjo (primeiro/último/repouso nas
cifras raspadas) — nunca inferi-lo da relação relativa entre o tom de Chediak e o cc_key.
