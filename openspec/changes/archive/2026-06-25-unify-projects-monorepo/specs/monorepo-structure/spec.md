## ADDED Requirements

### Requirement: Single repository with separated packages

The system SHALL live in one repository containing distinct packages — `cifra_core` (shared), `cifra_scraper` (Flask API), and `harmonic_analysis` (analysis + CLI + reports). `cifra_core` MUST NOT depend on the other two. The analyzer's domain and service layers MUST depend only on `cifra_core` (the `SongProvider` port), never on the scraper.

#### Scenario: Core has no outward dependencies
- **WHEN** the package layout is inspected
- **THEN** `cifra_core` imports neither `cifra_scraper` nor `harmonic_analysis`
- **AND** both of those packages may depend on `cifra_core`

#### Scenario: Analyzer core is decoupled from the scraper
- **WHEN** modules under `harmonic_analysis/domain` and `harmonic_analysis/services` are inspected
- **THEN** none of them import `cifra_scraper`
- **AND** they reach cifra data only through the `cifra_core` `SongProvider` port

#### Scenario: In-process adapter is an opt-in dependency
- **WHEN** the in-process provider is selected
- **THEN** only the composition root (CLI wiring) imports the scraper to construct `InProcessSongProvider`
- **AND** that dependency is gated behind the `[inprocess]` optional group, so a pure-HTTP install does not require the scraper

### Requirement: Unified packaging toolchain

The repository SHALL use a single packaging toolchain and dependency manifest for all packages, replacing the previous split of Poetry (analyzer) and pip `requirements.txt` (scraper).

#### Scenario: One manifest drives installation
- **WHEN** a developer installs the project from a clean checkout
- **THEN** a single documented command installs all packages and their dependencies
- **AND** there is no standalone `requirements.txt` competing with the unified manifest

### Requirement: Single commands for build, test, run, and deploy

The repository SHALL expose unified entry points to run the scraper service, run the analyzer CLI, run the test suite, and build the container image.

#### Scenario: Run the whole system from the repo root
- **WHEN** a developer follows the README from the repo root
- **THEN** documented commands exist to (a) start the scraper service, (b) run an analysis via the CLI, and (c) run all tests
- **AND** the CLI can analyze a song without a separate manual step to start the service (via the in-process provider)

#### Scenario: Documentation matches reality
- **WHEN** the unified README describes setup and commands
- **THEN** it references the actual toolchain, scraper technology (BeautifulSoup), API route prefix (`/api`), and CLI entry point
- **AND** contains no references to removed or never-present tooling (e.g. `pip install -r requirements.txt`, Selenium, `python -m cli.main`)
