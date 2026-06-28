## ADDED Requirements

### Requirement: Multi-key gold for modulating songs

The harness SHALL support songs annotated with multiple gold keys — a primary tonality and one or more secondary tonalities — so that genuinely modulating pieces (per Chediak's modulação por acorde pivô, p. 118) are evaluated against their full tonal structure rather than a single label.

For a modulating song:
- **Primary acerto** (partial): the detected key matches the primary gold.
- **Full acerto** (total): `dominant_regions` detects all gold keys as dominant regions.
- **Erro**: neither the primary nor any secondary gold key is detected.

Monotonal songs (single gold key) are unaffected — their evaluation logic is unchanged.

#### Scenario: Modulating song with correct primary detection counts as partial acerto
- **WHEN** a modulating song is evaluated and `detect_key` returns the primary gold key
- **THEN** the result is `primary_ok=True`
- **AND** it does NOT count as a full acerto unless all secondary keys are also found in `dominant_regions`

#### Scenario: Modulating song with all regions detected counts as full acerto
- **WHEN** `dominant_regions` for a modulating song contains regions matching both the primary and all secondary gold keys
- **THEN** the result is `all_ok=True` and `primary_ok=True`

#### Scenario: Monotonal evaluation is unchanged
- **WHEN** a song with a single gold key is evaluated
- **THEN** it uses the existing `KeyEval` logic (exact / relative / erro)
- **AND** no new fields are added to its evaluation record

#### Scenario: Modulating songs are reported separately in the baseline
- **WHEN** `key_baseline.py` runs
- **THEN** modulating songs appear in a separate section of the output with primary/full acerto indicated
- **AND** they are excluded from the aggregate monotonal metrics (mode %, exact %, relative-aware %) to avoid distorting the baseline
