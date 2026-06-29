# modal-center-arbitration Specification

## Purpose
TBD - created by archiving change modal-center-arbitration. Update Purpose after archive.
## Requirements
### Requirement: Modal center is a curated, display-time annotation, never detected from chords

The system SHALL expose a piece's **modal center** — a finalis (center note) plus a church mode (dorian, mixolydian, phrygian, aeolian, …) — as a **curated musicological fact** looked up by song identity (artist + title), rendered at **display time** as a cited curator note beside the algorithmic tonal reading. The annotation SHALL NOT be derived from the chords, SHALL NOT call `detect_key`/`detect_coloring`, SHALL NOT re-center or otherwise alter the tonal key, mode, scale degrees, harmonic functions, cadences, or any of the four Cifra-Club key metrics, and SHALL NOT mutate the analysis JSON. When no curated entry matches the song identity, no curator note is rendered and the report is byte-identical to one produced without this capability.

This is the **(B)** half of the analytical bifurcation: part **(A)** (`modal-mode-naming`) *names* the mode the algorithm can detect ("D mixolídio"); this capability *annotates* the center the chords cannot encode but the authority (Chediak) documents ("Lá dórico, p. 125").

#### Scenario: A curated song renders the curator note beside the tonal reading
- **WHEN** a song whose identity matches a curated modal-center fact is reported (e.g. Edu Lobo — Arrastão)
- **THEN** the report renders a "Nota do curador" carrying Chediak's modal center (finalis + church mode) and the arrangement-divergence caveat
- **AND** the tonal key, mode, scale degrees, functions, cadences, and the four Cifra-Club metrics are exactly those produced without the annotation

#### Scenario: A non-curated song renders no curator note
- **WHEN** a song whose identity matches no curated fact is reported (the common case)
- **THEN** no curator note is rendered and the report is byte-identical to today's

#### Scenario: The annotation never reads the chords or mutates the analysis
- **WHEN** the curator note is built
- **THEN** it is derived only from the curated dataset and the analysis identity (artist + title)
- **AND** `detect_key`/`detect_coloring` are not invoked and the analysis dict is not mutated

### Requirement: The curated dataset is a single typed source of citable facts with a mandatory citation

The curated modal centers SHALL live in **one** typed source (`harmonic_analysis.corpus.modal_centers`), holding only **facts** — artist, song, finalis, church mode, the transposition-safe `finalis_from_tonal` interval, a page citation, and a divergence note — never the book's chords, harmonizations, or text. Each fact SHALL carry a structurally **mandatory** `Citation` (source + volume + page): a fact cannot be constructed without it, and a malformed citation SHALL fail at import. The pre-existing `TIER_A_CHEDIAK` facts SHALL read from this single source rather than duplicating them. The dataset SHALL cover **center-divergence cases only** (the finalis differs from the detected tonal center); mode-name-only divergences (center already correct) belong to part (A) and SHALL be excluded.

#### Scenario: A fact cannot exist without a valid citation
- **WHEN** a `ModalCenterFact` is constructed without a `Citation`, or with an empty source / invalid page
- **THEN** construction fails (a `TypeError` for the missing citation, a `ValueError` for a malformed one) and the build does not pass

#### Scenario: Only genuine center-divergence cases are curated
- **WHEN** a song's true center already coincides with the detected tonal center and only the mode name diverges (e.g. Upa Neguinho, Pra Não Dizer)
- **THEN** it is NOT in the curated dataset (it is part (A)'s concern)
- **AND** a curated fact is present only when the finalis genuinely diverges (e.g. Arrastão, Procissão)

### Requirement: Identity matching is slug-normalized and the citation has a single formatter

Lookup SHALL key on `slug(artist) + "|" + slug(song)` reusing `cifra_core.slug`, so accent and casing variants ("Arrastao"/"Arrastão", "edu lobo"/"EDU LOBO") resolve to the same fact and a miss returns `None` (degrading to no note, never a wrong note). The citation string SHALL be produced by a **single** formatter (`format_citation`) yielding "Almir Chediak, Harmonia & Improvisação, Vol. I, p. 125" (Roman volume), consumed by both the Markdown and HTML renders so they never diverge; the JSON report SHALL carry the **structured** citation (`source`/`volume`/`page`), not the assembled string.

#### Scenario: Accent and casing variants resolve to the same fact
- **WHEN** the lookup is queried with "Arrastão" or "arrastao", "Edu Lobo" or "EDU LOBO"
- **THEN** it resolves to the same curated fact
- **AND** an unknown song misses cleanly (returns `None`)

#### Scenario: Markdown and HTML share one citation formatter
- **WHEN** the curator note is rendered in Markdown and in HTML
- **THEN** both display the same citation content ("Almir Chediak, Harmonia & Improvisação, Vol. I, p. 125") from the single formatter
- **AND** the JSON report carries the structured citation fields, not the assembled string

