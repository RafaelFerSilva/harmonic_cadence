## ADDED Requirements

### Requirement: Baseline documents expected accuracy after each calibration change

After any recalibration of key-detection parameters (weights, band thresholds), the project SHALL run `scripts/key_baseline.py` against the full corpus (n≥60, chords fetched live) and record the resulting metrics — mode, exact, and relative-aware accuracy — in `ROADMAP.md`. A song that previously produced an error result and now produces an exact or relative match MUST be explicitly noted as a resolved case.

#### Scenario: Recalibration is followed by a baseline run

- **WHEN** a key-detection parameter (e.g. `TIE_BAND`) is changed
- **THEN** the baseline script is executed before the change is archived
- **AND** the new metrics are committed to `ROADMAP.md`

#### Scenario: Resolved cases are recorded

- **WHEN** a song transitions from an incorrect detection to a correct one after a parameter change
- **THEN** it is noted in `ROADMAP.md` as a resolved case for that change
- **AND** the previous metric baseline is documented alongside the new one to show the delta

#### Scenario: No regressions are introduced

- **WHEN** the baseline is run after a parameter change
- **THEN** no song that was previously detected correctly transitions to an incorrect detection
- **AND** if a regression is found, the parameter change is rolled back or adjusted before archiving
