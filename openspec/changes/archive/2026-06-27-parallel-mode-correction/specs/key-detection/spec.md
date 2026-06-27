## ADDED Requirements

### Requirement: Parallel mode correction at the anchored tonic

The analyzer SHALL correct a parallel mode confusion (same tonic, major ↔ minor) by inverting the detected mode when, at the tonic the piece is anchored on, the quality of the tonic chords contradicts the Krumhansl-Schmuckler mode. The cadence cannot distinguish parallel keys (the dominant is shared — `G7` is the V of both C major and C minor), so the discriminator is the quality of the tonic-rooted chords (the third of the tonic defines the mode). The correction acts only when the detected tonic is the tonal anchor — the final bass is that tonic, or an authentic cadence (the dominant or its tritone substitute) resolves to it — and the net tonic-chord quality vote (minor minus major) is decisive. This bass-anchor gate keeps the correction from touching a relative-confusion case, where the detected tonic is an impostor.

The correction adjusts only the mode (the tonic from K-S is kept), composes with the cadential tie-break (which decides the tonic), and preserves the `KeyEstimate` shape; downstream mode-vs-key arbitration and segmentation are unchanged.

#### Scenario: A minor piece read as parallel major is corrected

- **WHEN** the K-S estimate is a major key but the piece is anchored on that tonic (settles on it or cadences to it) and the tonic chords are predominantly minor (e.g. an end like `G7 → Cm` over recurring `Cm`)
- **THEN** the detected mode is corrected to minor (the parallel)
- **AND** the detected tonic is unchanged

#### Scenario: A relative-confusion impostor tonic is not touched

- **WHEN** the detected tonic is NOT the anchor (the piece cadences elsewhere, e.g. detected A minor but the cadence resolves to C)
- **THEN** the parallel mode correction does not fire
- **AND** the mode is left as the K-S/tie-break result

#### Scenario: A major piece with isolated minor borrowings is not flipped

- **WHEN** a major key is anchored on its tonic but only an isolated minor tonic chord appears (the net tonic-quality vote is below the threshold)
- **THEN** the mode stays major

#### Scenario: Result shape and contract preserved

- **WHEN** `detect_key` returns an estimate after a mode correction
- **THEN** it is the same `KeyEstimate` shape, with the score reflecting the corrected key
- **AND** existing callers reading key/mode/alternatives continue to work
