## ADDED Requirements

### Requirement: Mode-aware tonal estimate

The key estimate SHALL be able to report a church mode (beyond `major`/`minor`) when the diatonic collection and tonal center indicate one, in coordination with `modal-tonal-center`. The existing major/minor detection and its result shape MUST remain valid.

#### Scenario: Modal piece reports its mode
- **WHEN** key detection runs on a clearly mixolydian progression centered on G
- **THEN** the estimate exposes a mode of `mixolydian` for that center

#### Scenario: Tonal piece still reports major or minor
- **WHEN** key detection runs on a standard tonal progression with a leading tone
- **THEN** the estimate's mode is `major` or `minor` as before
- **AND** existing callers reading the major/minor result continue to work
