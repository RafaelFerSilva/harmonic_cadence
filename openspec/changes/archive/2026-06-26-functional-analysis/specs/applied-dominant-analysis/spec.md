## ADDED Requirements

### Requirement: Dominant-quality chords without dominant function

The analyzer SHALL recognize that a dominant-seventh-quality chord which does NOT resolve as `V7→I` or `SubV7→I` may carry a non-dominant function determined by context, and SHALL classify it accordingly rather than defaulting to a secondary dominant. Per Chediak (pp. 111–113): `bVII7` is a minor subdominant (modal interchange in a major key); `I7` and `IV7` are blues chords; a `VII7` resolving directly to `I` is cadential (otherwise `V7/III`); `II7` and `bVI7` are altered subdominants related by tritone.

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
