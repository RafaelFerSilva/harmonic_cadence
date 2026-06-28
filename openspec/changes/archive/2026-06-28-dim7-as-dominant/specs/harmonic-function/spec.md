## ADDED Requirements

### Requirement: Diminished sevenths acting as rootless dominants carry dominant function

The analyzer SHALL assign the **dominant** function to a diminished-seventh chord that acts
as a rootless `V7(b9)` (i.e. resolves a semitone above its written root, per
applied-dominant-analysis), including when the chord is chromatic (non-diatonic to the key).
This extends the diatonic rule — under which `vii°7` already carries dominant function by
its degree (Chediak Vol. I p. 96) — to the chromatic ascending diminished chords
(`#i°7`, `#ii°7`, `#iv°7`) that function as secondary rootless dominants. A diminished
chord of approach/passing (one that does NOT resolve as a rootless dominant) SHALL NOT be
assigned dominant function.

#### Scenario: Diatonic vii°7 keeps its dominant function
- **WHEN** in C major `B°7` (degree `vii°7`) is classified
- **THEN** it is assigned the dominant function

#### Scenario: A chromatic ascending diminished acting as a secondary dominant is dominant
- **WHEN** in C major `C#°7` resolves to `Dm` (acting as `V7(b9)/ii`)
- **THEN** it is assigned the dominant function
- **AND** this holds even though `C#°7` is not diatonic to C major

#### Scenario: A passing diminished has no dominant function
- **WHEN** a diminished-seventh chord does not resolve a semitone above its root (a passing/auxiliary diminished)
- **THEN** it is NOT assigned the dominant function on that basis
