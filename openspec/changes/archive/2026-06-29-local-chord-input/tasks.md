# Tasks — local-chord-input

> Additive input adapter: analyze chords from a local `.txt`/string through the UNCHANGED engine.
> Reuses `clean_cifra_lines` + `ChordPattern` + `AnalysisService.analyze_song_data_structured`
> (already source-agnostic). Does NOT touch `detect_key`, the travas, `modal_coloring`, the
> corpora, or the `SongProvider` port.

## 1. Ingestion (text → normalized Cifra)

- [x] 1.1 Add `cifra_from_text(text, *, artist="", title="") -> Cifra` to `cifra_core` (beside `Cifra` + `clean_cifra_lines`): split text into lines, apply `clean_cifra_lines` ONCE (idempotent contract), build a `Cifra(artist, name=title, cifra=tuple(lines), key="")`. Use `clean_text`/`decode_unicode_escape` for encoding robustness. Export it from `cifra_core.__init__`.
- [x] 1.2 No parallel parser: ingestion produces clean LINES only; chord extraction stays the engine's job (`ChordPattern` via `_extract_chords`).

## 2. CLI entry (analyze a local file)

- [x] 2.1 Add a CLI subcommand `analyze-file <path> [--artist X] [--title Y]` (decide subcommand vs `--file` at build, design D4) in `cli/main.py`: read the file as UTF-8 (tolerant fallback), call `cifra_from_text`, then `AnalysisService.analyze_song_data_structured(cifra.to_dict())` and `ReportFactory` — built WITHOUT a network provider (no scrape/cache).
- [x] 2.2 Visible degradation: file-missing / empty / no-valid-chords → clear message + non-zero exit (reuse the engine's `success:False` errors). Default artist/title from the filename when flags absent.

## 3. Tests

- [x] 3.1 Ingestion unit tests: clean text → chords preserved; noise/section/blank lines filtered; idempotence (clean→clean unchanged); empty/garbage → empty lines; `key==""`; identity defaults.
- [x] 3.2 Engine-parity test: the same chord sequence via `cifra_from_text` and via a fake provider dict yields identical detected key + degrees + functions (the core is source-agnostic).
- [x] 3.3 CLI test: `analyze-file` on a temp file produces a report and constructs no network provider; a missing/empty file exits non-zero with a clear error.

## 4. Quality gate + docs

- [x] 4.1 `make test` green; `make lint` clean. `openspec validate local-chord-input --strict` passes.
- [x] 4.2 Update the CLI README + AGENTS.md: document the local-file path and that local input is metadata-free (key detected from chords; not scored by the Cifra-Club baseline). Then `openspec archive`.
