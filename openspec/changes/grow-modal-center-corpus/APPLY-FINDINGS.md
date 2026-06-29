# Apply findings — modal-section examples fully mined, no new fact committable

**Date:** 2026-06-29. **Method:** the admission protocol (spec) run live. Recorded the
baseline trava (task 1.1), read Chediak Vol. I pp.125-127 (§XXXVI.4 "Exemplos de músicas
populares em alguns modos" — the canonical modal-example set), partitioned the examples, and
probed each non-seed candidate against the live Cifra Club scrape.

## Baseline trava (task 1.1 — zero-regression reference)

`modo 86% · tônica exata 76% · relativa 83% · coleção 97% · centro TONAL 100% (19/19) ·
modulantes 100%`. Modal coverage `n=2` (Arrastão +7 p.125; Procissão +3 p.126).

## The complete modal-example set (pp.125-127) and its verdict

| Ex. | Song | Chediak | Verdict |
|---|---|---|---|
| a) iônico | **Cravo e Canela** (Milton N.), p.125 | Sol iônico (G) | **Excluded** — ionian = major; center = the major tonic, no divergence (offset 0). Also unresolved on CC. |
| b) dórico | **Arrastão** (Edu Lobo), p.125 | Lá dórico (A) | **Already in corpus** (+7). |
| c) mixolídio | **Upa Neguinho** (Edu Lobo), p.126 | Ré mixolídio (D) | **Rejected** — center already detected D; mode-name-only → part (A). |
| c) mixolídio (Ex.2) | **Procissão** (Gilberto Gil), p.126 | Dó mixolídio (C) | **Already in corpus** (+3). |
| d) eólio | **Pra não dizer…** (Geraldo Vandré), p.127 | Mi eólio (E) | **Rejected** — center already correct in the arrangement; aeolian = natural minor; mode-name-only → part (A). |
| e) lídio b7 | **Gravidade** (Caetano Veloso), p.127 | Dó lídio b7 (C) | **Only genuine new center-divergence candidate — but BLOCKED BY DATA.** |

## Why Gravidade is blocked by data (not mechanism)

Gravidade is the one example that would be a real center divergence (a I7 lydian-dominant tonic;
the tonal axis would not land on C). But **Cifra Club has no chord chart for it** — only the
lyrics page `https://www.cifraclub.com.br/caetano-veloso/565091/letra/` (a numeric-ID `/letra/`
URL; the artist-slug song URL redirects to the artist page). The scraper correctly returns
`EmptyCifra`.

Consequences, by the Golden Rule:
1. There is **no scraped substrate** to curate `finalis_from_tonal` from (design D2 requires the
   interval be read from Chediak's analysis *onto the scraped chords*, anchored to the detected
   tonal center — there are no chords).
2. Even if the interval were curated from the book alone, the curator note would **never render**:
   the pipeline annotates a song only when its scraped chords are analyzed, and Gravidade cannot
   be analyzed (no chords). The fact would be **dead data**.

Per the admission protocol, an unresolved candidate is **deferred, never guessed**. Gravidade
is deferred — reopen if/when a chord chart for it exists (CC contribution, or a curated
chord source).

## Conclusion

The clean, copyright-safe source (the modal-example section) is **fully mined and yields no new
committable fact**: two are already in the corpus, two are mode-name-only (part A), one is
tonal-ionian, and the only genuine new center-divergence (Gravidade) has no chord substrate on
Cifra Club. This is exactly the **data-gating the design anticipated (D3)** — the machinery is
correct; growth waits on data.

Next legitimate source would be the Parte 4 song analyses (pp.189-282, 295-317), but those are
⚠ copyright-sensitive (the analyses, not bare facts) and each candidate would still need (a) a
scrapable CC chord chart and (b) a confirmed center divergence — a larger, separate curation
effort to scope with the user.

## Parte 4 verification (user chose "expand to Parte 4") — it is TONAL, not modal

Sampled the major-tonality analyses (e.g. "PALCO", Gilberto Gil) and confirmed the format:
every analyzed song carries a header **"Tom de X maior/menor"** + a `[X MAIOR]`/`[X MENOR]`
box. Parte 4 is organized as **tonalidade maior (II.A) / menor (II.B)** — **tonal analyses by
construction**. There is no modal section in Parte 4; Chediak assigns explicit *modal* centers
(finalis + church mode) ONLY in §XXXVI.4 (the modal section, already exhausted).

Implication for THIS corpus (`modal_centers`):
- A Parte 4 "Tom de X" is the **tonal tonic**, i.e. `structural_offset = 0` for us when
  `detect_key` agrees — **no modal-center divergence to annotate**.
- A case where `detect_key` *disagrees* with Chediak's cited tonal tonic is a **tonal detector
  miss** (a bug to fix / the tonal center hole), NOT a curated *modal* fact. Filing it in
  `modal_centers` (finalis + church mode) would be a category error.

So **Parte 4 cannot grow the modal corpus.** What it CAN feed is a different artifact: the
**tonal structural-center gold** (`scripts/chediak_structural_gold.py`, the `chediak`
provenance tier) — Chediak's cited "Tom de X" as a tonal-center anchor, which would expand
center coverage beyond the 19 verified-by-dominant and surface detector holes. That is a
separate change (capability `key-accuracy-evaluation`, tonal center), not this one.

## Net conclusion

The `modal_centers` corpus is genuinely **data-gated at n=2**: Chediak's named modal pieces
with a scrapable CC chord chart are exhausted (Gravidade, the one remaining, has no CC chords).
Growing it further needs new DATA (a chord substrate for Gravidade, or modal pieces Chediak
names that we haven't found), not more mining of the tonal Parte 4.
