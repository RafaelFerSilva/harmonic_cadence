## Context

This change was first designed as **detection** (Caminho 1): a `modal_center.py` domain
module reading the chords and gating on absence-of-dominant + modal-cadence-to-finalis to
**recover** the modal center. The zero-regression trava invalidated that premise before any
code shipped — see [PROBE-FINDINGS.md](./PROBE-FINDINGS.md): Arrastão's finalis (Lá) is
**unrecoverable** from the Cifra Club chords (`_central_pc`→Mi, the piece ends on `D7+`, Lá
only ties for 2nd), and Procissão's Dó appears **1×/80**. Per the project's Golden Rule
([[modal-center-blocked-by-corpus]]), a detection target is implementable only if the raw
data encodes it — and it does not.

This redesign pivots to **Caminho 2 — annotation, not detection**. The modal center for the
genuinely-divergent pieces is a **curated musicological fact** (Chediak's reading, with page
citation), injected at **display time**, that never reads the chords for a verdict, never
touches `detect_key`, and never enters a detection-accuracy metric. It is the exact same
display-layer pattern as the just-shipped part **(A)** `modal-mode-naming` ([[session-handoff-3b]]):
(A) **names** what the algorithm detects ("D mixolídio"); (B) **annotates** what the data
cannot encode but the authority documents ("Chediak p.125: Lá dórico"). Together they are the
**explicit analytical bifurcation** — the algorithm's truth and the literature's truth, side
by side.

The unlock the ROADMAP missed: Caminho 2 needs a **curated *fact* corpus** (artist→song→
center→mode→page→note), which is cheap and copyright-safe — **not** a melodic substrate
(MIDI/MusicXML), which is the legal/technical quagmire that blocked Caminho 1. The block was
never "we lack the answer" (Chediak gives it); it was "no mechanism recovers it from chords."
Annotation sidesteps the mechanism entirely.

## Goals / Non-Goals

**Goals:**
- Display Chediak's modal center (finalis + church mode) as a cited **curator note**, side by
  side with the algorithmic tonal reading, for pieces where the two genuinely diverge
  (Arrastão → Lá dórico; Procissão → Dó mixolídio).
- Keep a **single curated source of truth** for the modal facts (no duplication of the four
  facts already inert in `TIER_A_CHEDIAK`).
- Be **transposition-honest**: never present Chediak's absolute letter as if it shared the CC
  arrangement's key; express the divergence in a frame that survives transposition.
- Replace the (now meaningless) detection-accuracy metric with a **coverage + divergence
  ledger** reported live in the baseline — honest about the fact that *nothing is detected*.
- Guarantee, by construction, **zero movement** of the four Cifra-Club metrics and the tonal
  `center_accuracy`.

**Non-Goals:**
- Any chord-reading gate, finalis recovery, or `modal_center.py` domain module (Caminho 1 —
  abandoned).
- Touching `detect_key`, `detect_coloring`, `segment_keys`, `TIE_BAND`, functions, cadences,
  or any tonal metric (inviolable).
- Mode-**name**-only divergences (Upa Neguinho, Pra Não Dizer) — their center is already
  correct; naming the mode is part **(A)**'s job, not a curated annotation (see D4).
- A melodic substrate, or a large modal corpus — the annotation grows fact-by-fact as a
  musician curates, starting from the ~2 genuine center-divergence cases.

## Decisions

### D1 — Annotation at the display layer, not a domain detector

Drop `domain/modal_center.py` and `arbitrate_modal_center(symbols, …)` entirely. The modal
center is **looked up by song identity** (artist + title), not computed from symbols. The
lookup + render lives in the **presentation layer**, mirroring how part (A) wired
`modal_mode_name` into the report header ([markdown.py `_generate_header`](packages/harmonic_analysis/src/harmonic_analysis/presentation/reports/markdown.py), [html.py `_generate_html_document`](packages/harmonic_analysis/src/harmonic_analysis/presentation/reports/html.py)).

*Why*: there is no chord-derived verdict to make — the value is a cited fact. A domain gate
would re-import the invalidated premise (and the spurious-phrygian risk that got
`detect_mode` removed in `fix-or-remove-church-mode`). Display-only ⇒ **zero** detection-path
risk by construction.

### D2 — One curated source of truth (promote `TIER_A_CHEDIAK`)

The four facts already exist, inert, in [`scripts/chediak_structural_gold.py::TIER_A_CHEDIAK`](scripts/chediak_structural_gold.py)
(artist, song, center, mode, page, note — "RESERVADO para a change 2"). Rather than add a
parallel `curated_gold.json` that duplicates them (violating the project's "uma fonte" law),
**promote** that list into a single curated dataset that serves **both** the display
annotation **and** the metric.

Open recommendation (capture the user's call): a **Python module**
`scripts/curated_modal_centers.py` (or `packages/.../presentation/curated_modal_centers.py` if
the runtime report needs it without `scripts/` on the path) keeps parity with
`key_baseline.GOLD` and `TIER_A_CHEDIAK` (typed, test-visible, no JSON parse/validate layer). A
`curated_gold.json` is viable if non-developer editing is wanted, but then it must be the
**only** copy and `TIER_A_CHEDIAK` reads from it. Either way: **one** source. Copyright
boundary unchanged — facts only (no chords, no book text/tables).

Schema per entry (extends the existing tuple with the transposition-safe field from D5):
```
artist, song            # identity key (slugified, reuse cifra_core/slug.py)
curated_center          # Chediak's finalis letter, in CHEDIAK'S edition (e.g. "A")
curated_mode            # church mode (e.g. "dorian")
finalis_from_tonal      # D5: semitone interval finalis−(detected tonal center), IN THE
                        #     CC ARRANGEMENT; curated by reading Chediak's analysis onto
                        #     the scraped chords — NOT chediak_center_pc − cc_key_pc
page                    # Chediak Vol. I page
note                    # the divergence explanation (arrangement transposed/tonalized)
```

### D3 — Scope is identity-keyed; reuse the slug machinery

Lookup key = `slug(artist) + "|" + slug(song)` via [`cifra_core/slug.py`](packages/cifra_core/src/cifra_core/slug.py),
the same normalization the provider/baseline already use, so "Arrastao"/"Arrastão" and
artist-casing variants resolve. A miss ⇒ no curator note (the common case; the report is
byte-identical to today).

### D4 — Curated annotation covers CENTER divergence only; mode-name divergence is part (A)

The clean partition that fell out of explore:

```
  offset == 0  (center already correct, only the mode NAME differs)
      → Upa Neguinho (D mixo), Pra Não Dizer (E aeolian)
      → handled ALGORITHMICALLY by part (A) modal-mode-naming / coloring
      → NOT in the curated set

  offset != 0  (the center itself diverges; chords cannot encode the finalis)
      → Arrastão (Lá dórico vs detected D maj), Procissão (Dó mixo vs detected A maj)
      → handled by CURATED ANNOTATION (this change, part B)
```

So the curated dataset holds **only** the genuine center-divergence cases. Pra Não Dizer and
Upa Neguinho stay out — annotating them would duplicate (A) and imply a divergence that isn't
there. (Their `cc_key` transposition mismatch is a separate baseline note, not a modal-center
fact.)

### D5 — Transposition honesty (the crux)

Chediak's "Lá dórico" lives in **Chediak's edition**; the scraped CC arrangement may be in a
different key (probe: Arrastão Chediak Lá, cc_key Sol, chords detect Ré maior — three frames).
Two rules:

1. **Never auto-transpose Chediak's absolute letter into the arrangement, then subtract** —
   `chediak_center_pc − cc_key_pc` is the exact trap that breaks Pra Não Dizer (Mi vs Fá). The
   metric's offset is **curated**, read from Chediak's functional analysis applied to the
   scraped chords (the `finalis_from_tonal` interval, anchored to the algorithm's own detected
   tonal center — the one frame computed from the real data), citing the page.
2. **Display presents Chediak's reading as the book's, explicitly labeled**, with the
   divergence stated — it does **not** silently render "Lá dórico" beside "Ré maior" as if
   commensurable. The note carries the caveat (arrangement adapted/transposed). Optionally the
   finalis may also be shown transposed into the arrangement via `finalis_from_tonal` ("≈ o
   modo dórico sobre o 5º grau da leitura tonal"), which IS transposition-safe; the absolute
   "Lá dórico (Chediak, p.125)" remains the citation.

### D6 — The metric is a divergence ledger + coverage, NOT detection accuracy

Caminho 1 proposed `modal_center_accuracy` over the `chediak` tier. Under Caminho 2 **nothing
is detected**, so an accuracy would be trivially 100% (we assert the gold) — dishonest. Replace
it with, in `validation/key_accuracy.py` + the baseline report:
- **Coverage:** "N songs carry a curated modal-center annotation."
- **Divergence ledger:** per curated song, `(detected tonal center, curated modal center+mode,
  finalis_from_tonal interval, page)` — quantifying the gap (e.g. "arranjo lê maior; Chediak
  concebe dórico uma 5ªJ acima"), which is the pedagogical payload itself.
This is degree-relative ([[center-eval-degree-relative]]) and transposition-safe by D5.

### D7 — Quarantine integrity (the inviolable gate)

The curated-modal songs are already outside the tonal `center_accuracy` (it runs over the
`verified` tier only, [key_accuracy.py:207](packages/harmonic_analysis/src/harmonic_analysis/validation/key_accuracy.py#L207))
and outside the four Cifra-Club metrics (which compare against `cc_key`, untouched). Because
this change adds only a display lookup + a separate ledger, **every** existing metric is
byte-identical. The trava re-runs `key_baseline.py` and diffs to prove it — the same gate that
barred two bad ships ([[tritone-gate-quality-lesson]]).

## Display shape (the bifurcation)

```
**Tonalidade sugerida:** D (maior)
**Centro modal:** D mixolídio                              ← (A), algorithmic surface

> **Nota do curador — Chediak, Harmonia & Improvisação Vol. I, p. 125:**
> Esta composição é concebida em **Lá dórico**. A cifra analisada (Cifra Club) está
> adaptada — em outra tonalidade e sem o sinal funcional do modo —, então a leitura
> algorítmica acima reflete o *arranjo*, não a *concepção* original.   ← (B), curated fact
```

The curator note renders **only** when an entry exists; otherwise the report is unchanged.

## Risks / Trade-offs

- **Tiny n (≈2).** Only Arrastão and Procissão are genuine center-divergence facts today. The
  feature is correct but low-coverage until a musician curates more. `log`/report the count so
  coverage is never overstated. *(Accepted: the architecture is the deliverable; facts accrue.)*
- **Arrangement-specific facts.** `finalis_from_tonal` is curated against the *scraped* chords;
  if CC re-arranges the song, re-curate. Flagged in the entry `note`. *(Accepted.)*
- **Identity-key brittleness.** Title/artist variants must slug-match; reuse `slug.py` and add a
  test. A miss degrades to "no note" (safe), never to a wrong note.
- **Provenance discipline.** Only facts (center/mode/page/note/interval) — never book text,
  tables, or chords. Same boundary as `key_baseline.GOLD` and `TIER_A_CHEDIAK`.

## Migration / Open Questions

- **D2 format — Python module vs JSON?** ✅ **Decided: typed Python module** (single source,
  test-visible, no parse/validate layer). Full typed contract in **Appendix A**.
- **Where does the curated loader live?** ✅ **Decided: under `packages/` (not `scripts/`)** —
  proposed `packages/harmonic_analysis/src/harmonic_analysis/corpus/modal_centers.py`. Rationale
  (Appendix A): `make lint` runs `ruff check packages` only (scripts/ is unlinted) and the
  runtime report must import it without a `scripts/` path hack. Both validation and presentation
  import from this one place; `TIER_A_CHEDIAK` is migrated to read from it.
- **Where is "citation mandatory" actually enforced?** The build has **no type checker in the
  gate** (`mypy>=1.10` is installed but `make lint` = `ruff check packages` only). So static
  typing is IDE ergonomics, not CI — the obligation is enforced at **runtime (`__post_init__`)
  + a pytest corpus invariant** (`make test` is the real gate). See Appendix A.
- **OPEN — promote mypy to the gate?** Adding `uv run mypy` to `make lint` (and extending
  ruff/mypy to `scripts/`) would upgrade `Literal[ChurchMode]` + "no-default citation" from
  IDE-only to static CI enforcement. Orthogonal to this change; decide separately.
- Whether to also render the transposition-safe relative finalis ("dórico sobre o 5º grau") in
  addition to the absolute citation (D5.2) — a presentation nicety, decide at build.

## Appendix A — D2 typed contract (mandatory citation, fail-fast)

The curated source is a typed Python module under `packages/` (decided above). Citation
(source + volume + page) is **structurally required**: an entry cannot be constructed without
it, and a malformed one fails at import. Defense in depth — the build goes red only when, and
exactly when, someone adds an uncited or malformed fact; valid additions stay green.

```python
# packages/harmonic_analysis/src/harmonic_analysis/corpus/modal_centers.py
from dataclasses import dataclass
from typing import Literal

ChurchMode = Literal["dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]


@dataclass(frozen=True, slots=True, kw_only=True)
class Citation:
    """Citação obrigatória — sem ela o fato não existe (muro de copyright = fatos citados)."""
    source: str          # "Almir Chediak, Harmonia & Improvisação"
    volume: int          # 1
    page: int            # 125

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Citation.source vazio: todo fato modal exige a obra.")
        if self.volume < 1:
            raise ValueError(f"Citation.volume inválido: {self.volume!r}")
        if self.page < 1:
            raise ValueError(f"Citation.page inválida: {self.page!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class ModalCenterFact:
    artist: str
    song: str
    curated_center: str          # finalis na edição de Chediak (ex. "A")
    curated_mode: ChurchMode
    finalis_from_tonal: int      # D5: intervalo (semitons) finalis − centro tonal detectado
    citation: Citation           # ← obrigatória, SEM default
    note: str = ""               # divergência de arranjo (pode ser vazia)

    def __post_init__(self) -> None:
        if not (0 <= self.finalis_from_tonal < 12):
            raise ValueError(f"finalis_from_tonal fora de 0..11: {self.finalis_from_tonal!r}")


CORPUS: tuple[ModalCenterFact, ...] = (
    ModalCenterFact(
        artist="Edu Lobo", song="Arrastao",
        curated_center="A", curated_mode="dorian", finalis_from_tonal=7,
        citation=Citation(source="Almir Chediak, Harmonia & Improvisação", volume=1, page=125),
        note="O arranjo do Cifra Club transpõe e omite o sinal funcional do dórico.",
    ),
    # Procissão (Dó mixolídio, p.126) — adicionar com a citação obrigatória.
)
```

**Enforcement layers:**

| Layer | Guarantees | Fires at | Breaks build? |
|---|---|---|---|
| `kw_only=True` + `citation` no default | citation cannot be omitted; named args prevent swapping `page`/`finalis_from_tonal` (both `int`) | construction | `TypeError` at import |
| `Citation.__post_init__` | citation not empty/invalid (source, volume≥1, page≥1) | module import | `ValueError` → pytest collection fails |
| `Literal[ChurchMode]` | misspelled mode flagged | IDE / mypy (if gated) | only if mypy enters the gate |
| **corpus invariant test** | the explicit CI gate | `make test` | **yes — the real obligation** |

```python
# packages/harmonic_analysis/tests/test_modal_corpus.py
import pytest
from harmonic_analysis.corpus.modal_centers import CORPUS, Citation, ModalCenterFact

@pytest.mark.parametrize("fact", CORPUS, ids=lambda f: f.song)
def test_every_fact_has_a_valid_citation(fact):
    assert isinstance(fact.citation, Citation)
    assert fact.citation.source.strip() and fact.citation.page >= 1

def test_citation_cannot_be_omitted():
    with pytest.raises(TypeError):           # sem citation → não constrói
        ModalCenterFact(artist="x", song="y", curated_center="A",
                        curated_mode="dorian", finalis_from_tonal=0)
```
