## MODIFIED Requirements

### Requirement: Dominant-quality chords without dominant function

The analyzer SHALL recognize that a dominant-seventh-quality chord which does NOT resolve as `V7→I` or `SubV7→I` may carry a non-dominant function determined by context, and SHALL classify it accordingly rather than defaulting to a secondary dominant. Per Chediak (pp. 111–113): `bVII7` is a minor subdominant (modal interchange in a major key); `I7` and `IV7` are blues chords; a `VII7` resolving directly to `I` is cadential (otherwise `V7/III`); `II7` and `bVI7` are altered subdominants related by tritone.

A dominant-seventh chord that matches NONE of the special functions and has NO functional
resolution SHALL NOT fall through to a repose function by degree position: a real tritone is
never tonic by position (the sole exception is the blues `I7`, p.112(3)). When such a chord's
root sits on the sixth, third, or flat-third degree (`VI7`, `III7`, `bIII7`), the analyzer
SHALL classify it as a **secondary dominant resolved deceptively** (`Dsec`, expected target
`(V7/x)` a perfect fourth above the root) — per Chediak p.114(1), when the expected diatonic
resolution does not happen the analysis remains that of a dominant, noted by its expectation.
This deceptive fallback SHALL apply only after every special-function and resolution branch
has failed, so no currently-classified chord changes label.

#### Scenario: bVII7 is a minor subdominant, not a secondary dominant
- **WHEN** in C major the chord `Bb7` resolves up a whole step to `C`
- **THEN** it is classified as a minor-subdominant / modal-interchange chord (`bVII7`)
- **AND** it is NOT labeled a secondary dominant

#### Scenario: Blues sevenths on I and IV are not secondary dominants
- **WHEN** in C major `C7` (`I7`) and `F7` (`IV7`) appear in a blues context
- **THEN** each is classified as a blues chord, not a secondary dominant

#### Scenario: VII7 resolving to the tonic is cadential
- **WHEN** in C major a long `B7` resolves directly to `C` and is not preceded by a ii cadential
- **THEN** it is classified as a cadential `VII7`
- **AND** a short `B7` in the `F#m7 B7` cliché is classified as `V7/III` instead

#### Scenario: A genuine secondary dominant is still detected
- **WHEN** in C major `E7` resolves to `Am`
- **THEN** it remains a secondary dominant targeting the sixth degree (`V7/vi`)

#### Scenario: A deceptive VI7 is a secondary dominant, never tonic

- **WHEN** in C major an `A7` (`VI7`) does not resolve to any functional target (e.g. it is
  followed by `C7M` or ends the piece)
- **THEN** it is classified `Dsec` as a deceptively-resolved secondary dominant with expected
  target `(V7/II)` (Chediak p.114)
- **AND** it is never classified as tonic (`T`) by its degree position

#### Scenario: A deceptive III7 is a secondary dominant, never tonic

- **WHEN** in C major an `E7` (`III7`) is followed by a chord other than its diatonic target
- **THEN** it is classified `Dsec` with expected target `(V7/VI)` — not `T`

#### Scenario: Special-function positions are untouched by the deceptive fallback

- **WHEN** in C major a `D7` (`II7`) or an unresolved `B7` (`VII7`) matches no existing branch
- **THEN** the deceptive fallback does NOT claim it (its Chediak reading is a special
  function — altered subdominant / cadential — handled by its own classification)
