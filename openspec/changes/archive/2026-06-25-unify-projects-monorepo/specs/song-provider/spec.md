## ADDED Requirements

### Requirement: SongProvider port abstracts cifra retrieval

The analyzer SHALL obtain songs and artist song-lists exclusively through a `SongProvider` port, and MUST NOT depend on a concrete HTTP client, URL, or scraper implementation in its service or domain layers.

#### Scenario: Analyzer depends on the abstraction
- **WHEN** `AnalysisService` needs the data for a song
- **THEN** it requests it from an injected `SongProvider` instance
- **AND** no module under `harmonic_analysis/domain` or `harmonic_analysis/services` imports `requests`, a hardcoded URL, or the scraper package directly

#### Scenario: Provider returns a typed song
- **WHEN** a `SongProvider.get_song(artist, song)` call succeeds
- **THEN** it returns the shared `Cifra` model (from `cifra-core`)
- **AND** the analyzer reads fields from that model rather than from loose dictionary keys

### Requirement: Provider errors are a typed, distinguishable taxonomy

Every `SongProvider` method SHALL raise only subclasses of `SongProviderError`, and each failure cause MUST map to a distinct subtype so a caller can branch on cause without parsing message strings. The taxonomy MUST distinguish *negative* outcomes (the item does not exist — do not retry) from *availability* outcomes (transient — retry or fall back to cache).

#### Scenario: Missing song raises SongNotFound
- **WHEN** `get_song` is called for an artist that exists but a song that does not
- **THEN** the provider raises `SongNotFound`
- **AND** `SongNotFound` is a subclass of `SongProviderError`

#### Scenario: Missing artist raises ArtistNotFound
- **WHEN** `list_artist_songs` (or `get_song`) is called for an artist that does not exist
- **THEN** the provider raises `ArtistNotFound`

#### Scenario: Lyrics-only song raises EmptyCifra
- **WHEN** `get_song` resolves a song that has no chart lines (lyrics-only or instrumental)
- **THEN** the provider raises `EmptyCifra`
- **AND** the `--all` flow treats this as a skip, not a hard failure

#### Scenario: Transport failure raises ProviderUnavailable
- **WHEN** the upstream is unreachable (connection error, timeout, or HTTP 5xx)
- **THEN** the provider raises `ProviderUnavailable`
- **AND** the caller can distinguish it from `SongNotFound`/`EmptyCifra`

#### Scenario: Unexpected upstream payload raises UpstreamError
- **WHEN** the upstream responds but the body cannot be parsed into a `Cifra` (malformed JSON or unexpected HTML)
- **THEN** the provider raises `UpstreamError`

#### Scenario: Callers can catch the whole family
- **WHEN** a caller wraps a provider call in `except SongProviderError`
- **THEN** every raisable provider error is caught by that single handler

### Requirement: HTTP adapter preserves current service-based behavior

The system SHALL provide an `HttpSongProvider` that fetches songs from the running Flask scraper service over HTTP, equivalent to today's `infra/cifra_api` behavior, mapping HTTP outcomes onto the error taxonomy.

#### Scenario: Fetch a song from the running API
- **WHEN** `HttpSongProvider.get_song(artist, song)` is called and the API is reachable
- **THEN** it requests `GET /api/artists/<artist-slug>/songs/<song-slug>`
- **AND** returns the parsed song

#### Scenario: HTTP 404 maps to SongNotFound
- **WHEN** the API responds with HTTP 404 for the requested song
- **THEN** the provider raises `SongNotFound`

#### Scenario: Connection error maps to ProviderUnavailable
- **WHEN** the API host cannot be reached or the request times out
- **THEN** the provider raises `ProviderUnavailable`

#### Scenario: Malformed body maps to UpstreamError
- **WHEN** the API returns a 200 response whose body is not valid song JSON
- **THEN** the provider raises `UpstreamError`

### Requirement: In-process adapter runs without the server

The system SHALL provide an `InProcessSongProvider` that produces a song by invoking the scraper's repository directly, without requiring the Flask service to be running.

#### Scenario: Analyze a song with no server running
- **WHEN** the CLI is configured to use the in-process provider and no HTTP service is listening on port 3000
- **THEN** `analyze` still produces a report for a valid artist/song
- **AND** no HTTP request to `localhost:3000` is made

#### Scenario: Repository returning None maps to SongNotFound
- **WHEN** the wrapped `CifraClubRepository.get_cifra` returns `None`
- **THEN** the in-process provider raises `SongNotFound`

#### Scenario: Empty chart maps to EmptyCifra
- **WHEN** the wrapped repository resolves a song whose cifra has no chart lines
- **THEN** the in-process provider raises `EmptyCifra`

#### Scenario: Scrape transport failure maps to ProviderUnavailable
- **WHEN** scraping the source site raises a connection error or timeout
- **THEN** the in-process provider raises `ProviderUnavailable`

### Requirement: Caching decorator provides offline fallback

The system SHALL provide a caching `SongProvider` decorator that persists successful results locally and serves them when the wrapped provider is unavailable, replacing today's ad-hoc local-JSON fallback.

#### Scenario: Serve from cache when provider is offline
- **WHEN** a previously fetched song exists in the local cache
- **AND** the wrapped provider raises a connection error
- **THEN** the decorator returns the cached song instead of failing

#### Scenario: Provider selectable by configuration
- **WHEN** the application starts
- **THEN** the active `SongProvider` (http vs in-process, cached vs uncached) is chosen from configuration
- **AND** changing the selection requires no edits to domain or service code

### Requirement: Cache policy governs network/cache ordering

The `CachingSongProvider` SHALL accept a `CachePolicy` (`NETWORK_FIRST`, `CACHE_FIRST`, `CACHE_ONLY`, `REFRESH`) that deterministically governs when the wrapped provider and the store are consulted. `NETWORK_FIRST` SHALL be the default and reproduce today's behavior.

#### Scenario: NETWORK_FIRST returns fresh and writes through
- **WHEN** policy is `NETWORK_FIRST` and the wrapped provider succeeds
- **THEN** the fresh result is returned
- **AND** it is written to the store (write-through) before returning

#### Scenario: NETWORK_FIRST falls back to cache when unavailable
- **WHEN** policy is `NETWORK_FIRST`, the wrapped provider raises `ProviderUnavailable`, and the key exists in the store
- **THEN** the cached result is returned instead of raising

#### Scenario: CACHE_FIRST serves cache without touching the network
- **WHEN** policy is `CACHE_FIRST` and the key exists in the store
- **THEN** the cached result is returned
- **AND** the wrapped provider is not invoked

#### Scenario: CACHE_FIRST hits the network only on a miss
- **WHEN** policy is `CACHE_FIRST` and the key is absent from the store
- **THEN** the wrapped provider is invoked
- **AND** a successful result is written to the store

#### Scenario: CACHE_ONLY never reaches the network
- **WHEN** policy is `CACHE_ONLY`
- **THEN** the wrapped provider is never invoked
- **AND** a cache miss raises `ProviderUnavailable` rather than scraping or calling HTTP

#### Scenario: REFRESH forces a rewrite even when cached
- **WHEN** policy is `REFRESH` and the key already exists in the store
- **THEN** the wrapped provider is still invoked
- **AND** the store entry is overwritten with the fresh result

### Requirement: Negative results are never cached

The `CachingSongProvider` SHALL persist only successful `Cifra` results. `SongNotFound`, `ArtistNotFound`, and `EmptyCifra` MUST propagate to the caller and MUST NOT be written to the store.

#### Scenario: SongNotFound is not stored
- **WHEN** the wrapped provider raises `SongNotFound`
- **THEN** nothing is written to the store for that key
- **AND** a subsequent call still consults the wrapped provider rather than returning a cached negative

#### Scenario: EmptyCifra is not stored
- **WHEN** the wrapped provider raises `EmptyCifra`
- **THEN** the error propagates and no store entry is created for that key

### Requirement: Cache writes are atomic

The `CacheStore` SHALL update entries atomically (write to a temporary file, then replace), so a concurrent reader never observes a partially written entry under the `--all` thread pool.

#### Scenario: Concurrent reader never sees a partial entry
- **WHEN** an entry is being written while another thread reads the same key
- **THEN** the reader observes either the previous complete entry or the new complete entry
- **AND** never a truncated or corrupt one

#### Scenario: Interrupted write leaves the store consistent
- **WHEN** a write fails midway (process or I/O interruption)
- **THEN** any previously stored entry for that key remains intact and readable
