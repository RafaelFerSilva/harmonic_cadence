## Context

The repo already realizes most of "ports and adapters": a `SongProvider` Protocol
([provider.py](packages/cifra_core/src/cifra_core/provider.py)) with in-process and HTTP
adapters, a composition root (`build_song_provider`), and a `--provider` flag. Crucially, the
core is **already metadata-trap-free**: `AnalysisService` computes the key via
`detect_key([chord symbols])` ([analysis_service.py:109](packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py#L109))
and never reads the Cifra Club `Tom:`; `cifra.key` is only report metadata + validation gold.

The analysis entry point `analyze_song_data_structured(data)` is **already source-agnostic** — it
takes a dict with `cifra` (lines) + optional `artist`/`name`, and the scrape path
(`analyze_song_from_api`) is just `provider.get_song(...).to_dict()` fed into it
([analysis_service.py:495-503](packages/harmonic_analysis/src/harmonic_analysis/services/analysis_service.py#L495-L503)).
So a local-text path is symmetric: build the same dict from a file, feed the same method. The
canonical, idempotent line filter `clean_cifra_lines` already exists in `cifra_core`
([lines.py:48](packages/cifra_core/src/cifra_core/lines.py#L48)).

## Goals / Non-Goals

**Goals:**
- Analyze harmony from a local `.txt` / raw string, through the **unchanged** engine.
- Reuse the existing normalization (`clean_cifra_lines`) and chord extraction (`ChordPattern`) —
  one ingestion, no parallel parser; output the same normalized shape as the provider.
- Keep the source out of the core: the file path lives at the edge (CLI + a thin ingestion),
  the engine is untouched.

**Non-Goals:**
- Touching `detect_key`, the travas, `modal_coloring`, the corpora, or the `SongProvider` port.
- Forcing files through `SongProvider.get_song(artist, song)` (a file has no catalog identity).
- A GUI/upload server, MusicXML/MIDI, or melody — plain chord text only.
- Scoring local input in the validation baseline (no Cifra Club gold; out of scope by design).

## Decisions

### D1 — A separate ingestion, NOT a third `SongProvider` adapter

The port is `get_song(artist, song)` + `list_artist_songs` — **catalog** semantics. A file has no
catalog and no `(artist, song)` lookup, so shoe-horning it into the port distorts the contract.
Instead, add a small **ingestion function** that converts text → the normalized `Cifra`/data and
feed it straight into `AnalysisService`. The provider port stays for browsable sources (CC, future
APIs); raw text is a parallel, simpler ingress to the **same** core. *Alternative rejected*: a
`FileSongProvider(get_song=read file)` — it would have to ignore/abuse `artist, song` and fake
`list_artist_songs`, leaking file semantics into a catalog contract.

### D2 — Ingestion reuses `clean_cifra_lines` exactly once (honor the "filtra uma vez" contract)

`analyze_song_data_structured` documents that lines arrive **already cleaned** (the provider
applies `clean_cifra_lines` once; the filter is idempotent). The ingestion must therefore apply
`clean_cifra_lines` itself, once, so a local file reaches the engine in the identical shape a
scraped page does. Chord extraction stays the engine's job (`_extract_chords` / `ChordPattern`),
not the ingestion's — the ingestion only produces clean *lines* + identity, never a verdict.

### D3 — `cifra_from_text(text, *, artist="", title="") -> Cifra`

Return a real `Cifra` (so `.to_dict()` feeds the existing method unchanged), with `key=""`
(no Cifra Club annotation — the key is detected). `artist`/`title` default to empty → the engine's
existing "desconhecido" fallback applies. Placing the function in `cifra_core` (beside `Cifra` and
`clean_cifra_lines`) keeps it provider-agnostic and reusable by any front-end. *Open*: whether it
also accepts a file path or only a string — keep it pure (string in); the CLI reads the file.

### D4 — CLI: a distinct `analyze-file` subcommand

Add `harmonic analyze-file <path> [--artist X] [--title Y]`, mirroring `analyze`'s report wiring
(`ReportFactory`, format flags) but building the service **without** a network provider (no scrape,
no cache). A separate subcommand reads more clearly than overloading `analyze` (whose first
positional is `artist`); it also signals "this path never touches the Cifra Club." *Alternative
considered*: `analyze --file` — viable but muddies the positional contract; decide at build if a
flag is preferred for UX symmetry.

### D5 — Visible degradation

File-not-found, empty file, and "no valid chords" return a structured `{"success": False,
"error": ...}` (the engine already emits the last two), surfaced by the CLI with a clear message
and non-zero exit — consistent with `_safe_section` + `diagnostics` observability. No silent
empty report.

## Risks / Trade-offs

- **Garbage/ambiguous text** (lyrics with stray capital letters parsed as chords). → `ChordPattern`
  already governs what counts as a chord; the existing "nenhum acorde válido" guard covers the
  empty case. Document that input should be chord lines (the same shape a cifra sheet has).
- **Encoding** of arbitrary files. → reuse `clean_text`/`decode_unicode_escape` from
  `cifra_core.lines` (already battle-tested on scraped bytes); read files as UTF-8 with a
  tolerant fallback.
- **Scope creep toward upload servers / formats.** → explicitly out (Non-Goals); this is plain
  chord text only, the smallest useful adapter.

## Migration Plan

Purely additive: a new ingestion + a new subcommand. No existing entry point, schema, provider,
or report changes behavior. The existing `analyze` (scrape) path is byte-identical. Rollback =
remove the subcommand + function. The trava is a regression run of `make test` (engine untouched)
— no baseline change is expected or relevant (local input is not in the corpus).

## Open Questions

- Subcommand vs `--file` flag (D4) — decide on CLI UX at build.
- Should the ingestion also accept stdin (`-`) for piping? Cheap to add; decide at build.
- Where the function lives — `cifra_core` (recommended, provider-agnostic) vs
  `harmonic_analysis.infra` (closer to the CLI). Lean `cifra_core` for reuse.
