## 1. Decisions (RESOLVED — 2026 best practices)

> All decided in design.md → Resolved Decisions. Locked, not open work.

- [x] 1.1 Toolchain: **`uv` workspaces** (replaces Poetry + pip)
- [x] 1.2 Git history: **preserve via `git subtree`**
- [x] 1.3 Name: **keep `harmonic_cadence`** as umbrella; scraper = internal package
- [x] 1.4 D3 contract: **API emits cleaned lines** + idempotent core filter
- [x] 1.5 Default CLI provider: **in-process**; HTTP opt-in via config
- [x] 1.6 Python: standardize on **`>=3.12`** across all packages

## 2. Monorepo skeleton (uv workspace)

- [x] 2.1 Create root `pyproject.toml` with `[tool.uv.workspace] members = ["packages/*"]`; set `requires-python = ">=3.12"`; commit initial `uv.lock`
- [x] 2.2 Move analyzer code under `packages/harmonic_analysis` (its own `pyproject.toml`, `uv_build` backend)
- [x] 2.3 Bring scraper in under `packages/cifra_scraper` via `git subtree add --prefix=packages/cifra_scraper <scraper> <branch>`
- [x] 2.4 Create `packages/cifra_core` with its `pyproject.toml` + `uv_build` backend
- [x] 2.5 Wire `[tool.uv.sources] cifra-core = { workspace = true }` in both consumers; depend on `cifra_core` only
- [x] 2.6 Confirm `cifra_scraper` and `harmonic_analysis` do not import each other directly

## 3. Extract `cifra_core` (single source of truth)

- [x] 3.1 Move `fix_encoding` into `cifra_core`; delete both duplicate copies
- [x] 3.2 Move the `Cifra` model into `cifra_core`
- [x] 3.3 Move the canonical chord regex into `cifra_core`
- [x] 3.4 Reconcile the two line filters into one canonical, **idempotent**, order-preserving filter in `cifra_core`
- [x] 3.5 Unify slug generation into `cifra_core.slugify`; remove `cifra_slug` and the scraper's inline slug-building
- [x] 3.6 Add `SongRef` model to `cifra_core`
- [x] 3.7 Point scraper and analyzer at `cifra_core`; remove the now-dead local copies
- [x] 3.8 Add tests: `fix_encoding` (mojibake/passthrough/undecodable), filter (idempotency, tab/marker removal, order, dedup), chord regex, `slugify`, `Cifra` round-trip/immutability/`is_empty`

## 4. `SongProvider` port + adapters

- [x] 4.1 Define the `SongProvider` Protocol + exception taxonomy (`SongProviderError` + `SongNotFound`/`ArtistNotFound`/`EmptyCifra`/`ProviderUnavailable`/`UpstreamError`) in `cifra_core`
- [x] 4.2 Implement `HttpSongProvider` (in `harmonic_analysis`) from today's `infra/cifra_api`: map 404→`SongNotFound`, transport→`ProviderUnavailable`, bad body→`UpstreamError`
- [x] 4.3 Implement `InProcessSongProvider` (in `cifra_scraper`) wrapping `CifraClubRepository`: None→`SongNotFound`, empty→`EmptyCifra`, scrape failure→`ProviderUnavailable`
- [x] 4.4 Implement `CachingSongProvider` + `CachePolicy` (NETWORK_FIRST/CACHE_FIRST/CACHE_ONLY/REFRESH); atomic `CacheStore`; never cache negatives
- [x] 4.5 Add `build_song_provider` composition root + config (http/in-process, cache policy); `[inprocess]` extra carries the scraper dep
- [x] 4.6 Rewire `AnalysisService` to depend on the injected `SongProvider`
- [x] 4.7 Remove direct `requests`/URL/scraper imports from analyzer domain & services
- [x] 4.8 Add provider contract tests (exception taxonomy, cache policies) + a "no server running" in-process analysis test

## 5. Eliminate double filtering

- [x] 5.1 Apply the D3 contract: filter in exactly one place end-to-end
- [x] 5.2 Remove the analyzer's second filtering pass over already-filtered lines
- [x] 5.3 Verify scrape→analyze produces identical chord extraction before/after

## 6. Unify packaging, build & run

- [x] 6.1 Move scraper deps into `packages/cifra_scraper/pyproject.toml`; delete `requirements.txt`
- [x] 6.2 Update Dockerfile to install via `uv sync` (use the `astral-sh/uv` base image / `uv` Docker pattern); keep `docker-compose up` working
- [x] 6.3 Provide single entry points (`uv run` scripts): start scraper, run CLI, run tests, build image
- [x] 6.4 Gate scraping deps behind optional groups on `harmonic_analysis` (`[http]` vs `[inprocess]`, `[reports]`)
- [x] 6.5 Smoke-test `docker-compose up` and a CLI analysis end-to-end

## 7. Documentation

- [x] 7.1 Write unified root README (setup, commands, architecture diagram)
- [x] 7.2 Fix scraper README (BeautifulSoup not Selenium; `/api` prefix in examples)
- [x] 7.3 Fix analyzer README (Poetry/unified tool not `requirements.txt`; `harmonic` not `python -m cli.main`)
- [x] 7.4 Document provider selection and the in-process "no server needed" workflow

## 8. Validation & rollback gate

- [x] 8.1 Full test suite green across all three packages
- [x] 8.2 `docker-compose up` + one HTTP-provider analysis pass
- [x] 8.3 One in-process-provider analysis passes with no server running
- [x] 8.4 Keep original repos untouched until 8.1–8.3 pass; then cut over
