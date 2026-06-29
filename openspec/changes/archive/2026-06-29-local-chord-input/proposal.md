## Why

Today the **only** way to feed the analyzer is `(artist, song) → scrape the Cifra Club`. That
couples the product to one external site and to *its* catalog semantics. The team raised this in
`cifra_adapter.md`: the Cifra Club should be a **substitutable input adapter**, not the only door.
The harmonic engine (K-S, the quality gate, the Chediak functional travas) is the inviolable
core; the source of chords is a peripheral concern.

Most of the decoupling is already done — there is a `SongProvider` port with two adapters, and
the core **already detects the key purely from the chords** (`detect_key`), never from the Cifra
Club `Tom:` field (that annotation is only report metadata + validation gold). The one missing
piece is a **non-Cifra-Club input path**: letting a user analyze a plain chord text / `.txt`
file. That turns the tool from an "internet reader" into an active **compositional/academic**
instrument — a musician can sketch their own progression and get a full functional analysis
(degrees, functions, cadences, modulations, modal coloring) with zero scraping — and it makes the
engine resilient to the site changing layout, blocking scrapers, or going down.

## What Changes

- Add a **local chord-text input adapter**: ingest raw chord text (a `.txt` file or a string)
  into the same normalized `Cifra`/data shape the provider produces, and run it through the
  **unchanged** `AnalysisService`. Reuses `cifra_core.clean_cifra_lines` (the canonical,
  idempotent line filter) and `ChordPattern` — no parallel parser.
- Add a CLI entry to analyze a file — e.g. `harmonic analyze-file <path>` (or `analyze --file
  <path>`) — wired to the same `AnalysisService` + `ReportFactory`, **bypassing** the
  `SongProvider` (a file has no catalog, so it is NOT forced through `get_song(artist, song)`).
- Optional metadata: `--artist` / `--title` flags (default to the filename / "desconhecido"),
  since a local file carries no catalog identity. No `Tom:` is read — the key is detected from
  the chords, exercising the engine's full analytic capacity (the "metadata-trap escape").

## Capabilities

### New Capabilities
- `local-chord-input`: analyze harmony from a **local chord source** (a `.txt` file or raw
  string) — ingested into the normalized internal format and run through the existing analysis
  engine — independent of the Cifra Club, with the key detected from the chords alone.

### Modified Capabilities
<!-- none — the analysis engine, detect_key, the travas, and the SongProvider port are untouched -->

## Impact

- **New code:** a small ingestion (`cifra_from_text(text, *, artist?, title?) -> Cifra`/data,
  applying `clean_cifra_lines` once) in `cifra_core` (or a `harmonic_analysis.infra` module), and
  a CLI subcommand wiring it to `AnalysisService.analyze_song_data_structured` +
  `ReportFactory`. Tests for ingestion (chord extraction, noise filtering, empty/garbage input)
  and the CLI path.
- **Reuses unchanged:** `clean_cifra_lines`, `ChordPattern`, `AnalysisService`
  (`analyze_song_data_structured` is already source-agnostic), `ReportFactory`, `detect_key`,
  every trava and report generator.
- **Does NOT touch:** `detect_key`, the quality gate / functional travas, `modal_coloring`, the
  curated corpora, or the `SongProvider` port and its two adapters.
- **Boundary clarity:** the validation harness (`key_baseline`) still depends on the Cifra Club
  `key` as anti-transposition gold — that is a *measurement scaffold*, not the product. Local
  input simply has no exact-tonic gold (it is not scored by the baseline); the analysis runs
  fully regardless.
- **Risk:** additive input path; zero risk to the analytic core. Failure modes (file missing,
  no valid chords) degrade visibly with a clear error, consistent with the project's
  observability convention.
