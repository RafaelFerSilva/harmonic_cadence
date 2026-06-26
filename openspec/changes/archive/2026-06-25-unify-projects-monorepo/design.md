## Context

Two repositories form a single logical pipeline:

```
cifraclub.com.br ──HTML──▶ cifraclub_scrap_api (Flask :3000/api) ──JSON──▶ harmonic_cadence (CLI/analysis)
```

Both are Python with Clean Architecture (domain / application(services) / infrastructure / interface). They already share a data contract (`{artist, name, cifra[], cifra_html, youtube_url, only_lyrics, ...}`) and already duplicate code:

- `fix_encoding` — byte-for-byte identical in both repos.
- Cifra line filtering — `cifra_utils.clean_cifra_lines/should_keep_line` (scraper) vs `infra/utils.filter_cifra_lines` (analyzer); overlapping rules that **disagree**, and run **twice** end-to-end.
- Chord regex — `is_chord_only_line` (scraper) vs `ChordPattern.CHORD` (analyzer).

Constraints: solo developer; scraper is Dockerized (pip, gunicorn, Flask 3, Python 3.12); analyzer is Poetry (Python ^3.10), no Docker; scraping is network-bound and slow; the scraper has value as a standalone service for other consumers.

## Goals / Non-Goals

**Goals:**
- One repository, one toolchain, single build/test/run/deploy entry points.
- Eliminate cross-repo duplication via a shared `cifra_core` package (one source of truth).
- Turn the `localhost:3000` coupling into a `SongProvider` port with HTTP and in-process adapters, so the CLI can run with OR without the service.
- Preserve the scraper as an independently deployable service.

**Non-Goals:**
- Improving music-theory correctness (key detection, modal analysis, secondary-dominant interval direction).
- Restoring the broken test suites (tracked separately; this change adds tests only for the new seams).
- Changing the public JSON shape returned by the scraper API.

## Decisions

### D1 — Monorepo with three packages over full in-process fusion
Layout: `packages/{cifra_core, cifra_scraper, harmonic_analysis}`. Dependencies point inward to `cifra_core` only.
- **Why:** scraping and analysis fail differently, change at different cadences, and carry different heavy deps (bs4/lxml vs weasyprint). A monorepo kills duplication and the "invisible dependency" while keeping the boundary.
- **Alternatives:** (a) Full in-process fusion — rejected: couples deps, loses the reusable service, blocks the CLI on slow scraping. (b) Separate repos + published `cifra-core` on PyPI — rejected: versioning/publishing overhead is overkill for a solo, two-package setup.

### D2 — `SongProvider` port + adapters + caching decorator
Define `SongProvider` in `cifra_core` (`get_song`, `list_artist_songs`). Adapters: `HttpSongProvider` (today's `infra/cifra_api` HTTP client) and `InProcessSongProvider` (wraps the scraper's `CifraClubRepository`). `CachingSongProvider` wraps either and persists results, replacing the ad-hoc local-JSON fallback. Selection by config.
- **Why:** removes the choice between HTTP and in-process — both are supported; the analyzer depends only on the abstraction. Textbook hexagonal; the existing code is already ~80% of each adapter.
- **Alternative:** keep the hardcoded HTTP client — rejected: perpetuates the invisible dependency and the 2-terminal dev friction.

### D3 — Filtering happens once, owned by `cifra_core`
Pick the contract: the scraper API returns **cleaned** lines (it already runs `clean_cifra_lines`); the analyzer stops re-filtering and trusts the contract. The canonical filter lives in `cifra_core` and MUST be idempotent so the in-process path (which both scrapes and analyzes) stays correct.
- **Why:** double filtering with divergent rules is a latent bug; one idempotent filter resolves it regardless of path.
- **Alternative:** filter only at analysis time and have the API return raw lines — viable, but breaks existing API consumers expecting cleaned output.

### D4 — Unify on `uv` workspaces (2026 best practice)
Adopt **`uv`** (Astral) as the single toolchain, replacing **both** Poetry (analyzer) and pip/`requirements.txt` (scraper). Rationale: in 2026 `uv` is the de-facto standard for Python packaging — a single Rust binary replacing pip/pip-tools/pipx/poetry/pyenv/virtualenv, 10–100× faster, with first-class **workspaces** for monorepos and a single committed `uv.lock`.
- Root `pyproject.toml` declares the workspace: `[tool.uv.workspace] members = ["packages/*"]`.
- Each package depends on the core via `[tool.uv.sources] cifra-core = { workspace = true }`.
- Build backend `uv_build`; dev tooling under `[dependency-groups]`; scraping/report extras under per-package `[project.optional-dependencies]`.
- The standalone `requirements.txt` is deleted; scraper deps move into `packages/cifra_scraper/pyproject.toml`.
- **Alternative:** Poetry — rejected: slower, weaker monorepo/workspace story, and against the 2026 market default; keeping pip-only for the scraper was never a unification.

## Risks / Trade-offs

- **Python floor mismatch (analyzer ^3.10 vs scraper image 3.12)** → standardize on 3.12 for the repo; confirm no 3.10-only assumptions remain.
- **Tooling migration breaks the Docker build** → keep `cifra_scraper` runnable in Docker; update the Dockerfile to install from the unified manifest; smoke-test `docker-compose up` before/after.
- **Git history loss during merge** → use `git subtree add` to bring `cifraclub_scrap_api` in with history preserved (see Migration Plan); fall back to a clean import only if history is not wanted.
- **In-process provider drags scraping deps (bs4/lxml) into CLI installs** → expose adapters behind optional-dependency groups (`[http]` vs `[inprocess]`) so a pure-HTTP CLI install stays lean.
- **Idempotency regressions in the shared filter** → add idempotency and golden-output tests in `cifra_core` as the seam is created.

## Migration Plan

1. Create monorepo skeleton (`packages/`, unified manifest) on a branch; analyzer code moves under `packages/harmonic_analysis`.
2. Bring the scraper in with history: `git subtree add --prefix=packages/cifra_scraper <scraper-remote-or-path> <branch>`.
3. Extract `cifra_core`: move `fix_encoding`, the canonical line filter, chord regex, and the `Cifra` model; point both packages at it; delete the duplicates.
4. Introduce `SongProvider` + adapters + caching decorator; rewire `AnalysisService` to the port; default the CLI to `InProcessSongProvider` (or HTTP) per config.
5. Unify packaging; update Dockerfile/compose/Makefile; remove `requirements.txt`.
6. Fix both READMEs; add seam tests (provider contract, filter idempotency).
7. **Rollback:** the change lives on a branch until `docker-compose up` and a CLI analysis both pass; original repos remain untouched until then.

## Resolved Decisions (2026 best practices)

All five prior open questions are now decided:

- **Toolchain:** `uv` workspaces (see D4) — replaces Poetry and pip.
- **Git history:** preserve via `git subtree add --prefix=packages/cifra_scraper <scraper> <branch>`; the scraper's commits are retained. No clean import.
- **Repo / umbrella name:** keep **`harmonic_cadence`** as the repository and product name (it is the value proposition); the scraper lives as the internal `packages/cifra_scraper`.
- **D3 contract:** the scraper API **emits cleaned lines** (producer owns its output contract); the analyzer trusts the contract and the `cifra-core` filter is idempotent so the in-process path stays correct.
- **Default CLI provider:** **`InProcessSongProvider`** by default (best DX — analyze with one command, no server to start); `HttpSongProvider` is opt-in via config for the shared-service / scale scenario. Scraping deps (bs4/lxml) sit behind an optional group so a pure-HTTP install stays lean.

### Concrete target layout

```
harmonic_cadence/                  # repo + product name (unchanged)
├── pyproject.toml                 # [tool.uv.workspace] members = ["packages/*"]
├── uv.lock                        # single committed lockfile
├── docker-compose.yml             # runs cifra_scraper
└── packages/
    ├── cifra_core/                # encoding, idempotent line filter, chord regex,
    │                              #   Cifra model, SongProvider port
    ├── cifra_scraper/             # Flask API (BeautifulSoup); deps: [project] here
    │   └── pyproject.toml
    └── harmonic_analysis/         # domain + CLI + reports; default in-process provider
        └── pyproject.toml         # optional-deps: [http], [inprocess], [reports]
```

Standardize `requires-python = ">=3.12"` across all packages (matches the scraper's Docker image; drops the analyzer's stale `^3.10` floor).

## Appendix: SongProvider interface (detailed design)

Detailed contract for decision **D2**. Grounded in the existing code: the analyzer's `infra/cifra_api.fetch_song_data`/`fetch_artist_songs` and the scraper's `CifraClubRepository.get_cifra`/`get_artist_songs`. Implements requirements in `specs/song-provider/spec.md`.

### A.1 — Placement & dependency direction

```
cifra_core  (depends on neither adapter)
├── models.py       Cifra, SongRef
├── exceptions.py   SongProviderError + subtypes
├── provider.py     SongProvider (Protocol)          ◄── THE CONTRACT
├── cache.py        CacheStore (Protocol) + JsonFileCacheStore
└── slug.py         slugify()  (today duplicated on both sides)
        ▲                                      ▲
        │ depends                              │ depends
  harmonic_analysis: HttpSongProvider    cifra_scraper: InProcessSongProvider
  AnalysisService(provider)              (wraps CifraClubRepository)
```

Rule: `AnalysisService` knows only `SongProvider`, `Cifra`/`SongRef`, and the exceptions — never `requests`, a URL, or the scraper.

### A.2 — Data models (`cifra_core.models`)

```python
@dataclass(frozen=True, slots=True)
class Cifra:
    artist: str
    name: str
    cifra: tuple[str, ...]          # already-cleaned lines (D3 contract)
    cifra_html: str = ""
    youtube_url: str = ""
    cifraclub_url: str = ""

    @property
    def is_empty(self) -> bool:     # no chart lines (lyrics-only / instrumental)
        return not self.cifra

    @classmethod
    def from_api(cls, d: Mapping[str, Any]) -> "Cifra": ...
    def to_dict(self) -> dict: ...

@dataclass(frozen=True, slots=True)
class SongRef:
    name: str
    slug: str
    url: str
    only_lyrics: bool               # already produced by scraper; lets --all skip
```

`frozen=True` + `tuple` → immutable, hashable, safe to share across the `--all` ThreadPoolExecutor.

### A.3 — Exception taxonomy (`cifra_core.exceptions`)

The contract's core: distinguish **"does not exist" (don't retry)** from **"unavailable" (try cache/retry)**.

```python
class SongProviderError(Exception): ...        # base
class SongNotFound(SongProviderError): ...     # HTTP 404 / scraper returned None
class ArtistNotFound(SongProviderError): ...   # artist does not exist
class EmptyCifra(SongProviderError): ...       # exists but no chart lines → --all SKIPS
class ProviderUnavailable(SongProviderError): ...  # ConnectionError/timeout/5xx → cache/retry
class UpstreamError(SongProviderError): ...    # responded, but unexpected HTML/JSON
```

Replaces today's catch-all `RuntimeError(str)`. Negatives (`SongNotFound`, `EmptyCifra`) are NEVER cached as truth. The `--all` loop reads as:

```python
try:
    cifra = provider.get_song(artist, song)
except (SongNotFound, EmptyCifra):
    skipped += 1
except ProviderUnavailable:
    raise                       # infra problem — may abort the batch
except UpstreamError as e:
    failed.append((song, e))    # log and continue
```

### A.4 — The port (`Protocol`, not ABC)

```python
@runtime_checkable
class SongProvider(Protocol):
    def get_song(self, artist: str, song: str) -> Cifra:
        """Accepts human names; adapter slugifies via cifra_core.slugify.
        Returns: Cifra with cleaned lines (D3).
        Raises: SongNotFound | ArtistNotFound | EmptyCifra
                | ProviderUnavailable | UpstreamError"""

    def list_artist_songs(self, artist: str) -> list[SongRef]:
        """Raises: ArtistNotFound | ProviderUnavailable | UpstreamError"""
```

Deliberate choices: **`Protocol`** (adapters need not import/inherit `cifra_core` — dependency points inward without coupling); **synchronous** (whole codebase is sync; `--all` parallelism is already ThreadPoolExecutor — async would add complexity for no gain); **`slugify` owned by `cifra_core`** (today duplicated as `cifra_slug` + scraper URL building).

### A.5 — Caching decorator (`cifra_core.cache`)

```python
class CacheStore(Protocol):
    def get(self, key: str) -> Cifra | None: ...
    def put(self, key: str, cifra: Cifra) -> None: ...   # ATOMIC WRITE

class CachePolicy(Enum):
    NETWORK_FIRST = auto()   # = today's behavior (network; fall back to cache)
    CACHE_FIRST   = auto()   # cache; hit network only on miss (offline/fast dev)
    CACHE_ONLY    = auto()   # never touches the network (deterministic CI/tests)
    REFRESH       = auto()   # force network + rewrite (= today's download --force)

class CachingSongProvider:                  # is-a SongProvider, wraps another
    def __init__(self, inner, store, policy=CachePolicy.NETWORK_FIRST): ...
```

`NETWORK_FIRST` flow for `get_song`:

```
get_song → key = slugify(a)/slugify(s)
  inner.get_song ── success ──▶ store.put (write-through) ──▶ return
       └─ ProviderUnavailable ─▶ store.get(key)? hit→return(stale) | miss→re-raise
       └─ SongNotFound/EmptyCifra/UpstreamError ─▶ re-raise (never cached)
```

Contract rules:
- Cache fallback happens **only** on `ProviderUnavailable`.
- `store.put` MUST be atomic (`tmp` + `os.replace`) — today's direct write races under the 4-thread `--all`.
- `JsonFileCacheStore(dir="data/")` reproduces today's `{artist_slug}_{song_slug}.json` behind a swappable interface (future: SQLite).
- `max_age` TTL optional; default no expiry (cifras rarely change).
- The four policies generalize today's scattered `use_local_fallback` (→ NETWORK_FIRST), `download_and_cache_song(force=True)` (→ REFRESH), and the desire to run offline (→ CACHE_FIRST/ONLY).

### A.6 — Adapter mapping to existing code

| Contract | Maps from (today) |
|---|---|
| `HttpSongProvider.get_song` → `GET {base}/api/artists/{aslug}/songs/{sslug}`; 404→`SongNotFound`; ConnectionError→`ProviderUnavailable`; JSON→`Cifra.from_api` | `infra/cifra_api.fetch_song_data` minus the fallback (now the decorator) |
| `HttpSongProvider.list_artist_songs` → `[SongRef]` | `fetch_artist_songs` |
| `InProcessSongProvider.get_song`: `get_cifra(a,s)` None→`SongNotFound`; empty→`EmptyCifra`; site ConnectionError→`ProviderUnavailable` | scraper `CifraClubRepository.get_cifra` |
| `InProcessSongProvider.list_artist_songs` → `[SongRef]` | scraper `get_artist_songs` |

### A.7 — Composition root (only place that knows config)

```python
def build_song_provider(cfg: ProviderConfig) -> SongProvider:
    inner: SongProvider = (
        InProcessSongProvider() if cfg.kind == "inprocess"
        else HttpSongProvider(cfg.api_base_url)
    )
    if cfg.cache_enabled:
        inner = CachingSongProvider(inner, JsonFileCacheStore(cfg.cache_dir), cfg.policy)
    return inner
```

CLI builds this at startup and injects `AnalysisService(provider)`. New flags map directly: `--provider http|inprocess`, `--no-cache`, `--refresh`, `--offline` (→ `CACHE_FIRST`). Domain/services never see `ProviderConfig`. A `RetryingSongProvider` (backoff on `ProviderUnavailable`) is the same decorator pattern — future extension, not MVP. Default `kind` is `inprocess` (decision D2 / Resolved Decisions).

`InProcessSongProvider` lives in `cifra_scraper` (cohesive with `CifraClubRepository`). Because the default is in-process, `harmonic_analysis` takes an **optional** dependency on `cifra_scraper` — exercised only here in the composition root, gated behind the `[inprocess]` extra. The analyzer's domain & service layers still import only the `cifra_core` port, so the dependency-direction rule in `monorepo-structure` holds: a pure-HTTP install (`[http]` extra) never pulls in the scraper.

### A.8 — What the contract closes vs. today

| Fragile today | Closed by the port |
|---|---|
| `RuntimeError(str)` for everything | typed taxonomy; caller distinguishes causes |
| Cache fallback baked into the HTTP client | separate decorator, reused by in-process too |
| `cifra_slug` duplicated on both sides | one `cifra_core.slugify` |
| Non-atomic cache write under 4 threads | contract requires `tmp`+`replace` |
| "Música sem cifra" as an error string | `EmptyCifra` → `--all` skips cleanly |
| CLI requires the API to be up | `InProcessSongProvider` default |
