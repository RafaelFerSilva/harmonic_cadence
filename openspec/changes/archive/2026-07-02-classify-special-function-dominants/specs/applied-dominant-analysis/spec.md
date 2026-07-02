## MODIFIED Requirements

### Requirement: Dominant-quality chords without dominant function

The analyzer SHALL recognize that a dominant-seventh-quality chord which does NOT resolve as `V7→I` or `SubV7→I` may carry a non-dominant function determined by context, and SHALL classify it accordingly rather than defaulting to a secondary dominant. Per Chediak (pp. 111–113): `bVII7` is a minor subdominant (modal interchange in a major key); `I7` and `IV7` are blues chords; a `VII7` resolving directly to `I` is cadential (otherwise `V7/III`); `II7` and `bVI7` are altered subdominants related by tritone.

**Functional resolution SHALL precede the modal-interchange reading**: a `bVII7`/`bVI7` that
resolves a perfect fourth up into a diatonic target (e.g. `bVII7→bIII` in a minor key) is a
secondary dominant (`Dsec`, `V7/x`) — the `Emp` reading applies only without functional
resolution (Chediak p.114 uses `Bb7→Eb` as a secondary-dominant example).

A `II7` that matches no dominant branch SHALL be classified as an **altered subdominant**
(`SD`, "Subdominante alterada (II7)") per the special-function table (Chediak p.113, quadro:
`II7` → "Subd. alt."). A `VII7` that resolves directly to the tonic remains cadential (`D`);
a `VII7` that does NOT resolve to the tonic SHALL be read as `V7/III` (`Dsec`, expected
target `(V7/III)`) per p.112(2) — deceptive when the third degree does not follow (p.114).

A dominant-seventh chord that matches NONE of the special functions and has NO functional
resolution SHALL NOT fall through to a repose function by degree position: a real tritone is
never tonic by position (the sole exception is the blues `I7`, p.112(3)). When such a chord's
root sits on the sixth, third, or flat-third degree (`VI7`, `III7`, `bIII7`), the analyzer
SHALL classify it as a **secondary dominant resolved deceptively** (`Dsec`, expected target
`(V7/x)` a perfect fourth above the root) — per Chediak p.114(1), when the expected diatonic
resolution does not happen the analysis remains that of a dominant, noted by its expectation.
This deceptive fallback SHALL apply only after every special-function and resolution branch
has failed, so no currently-classified chord changes label.

The **documented special functions** (quadro p.113: `I7`→blues tonic, `IV7`→blues
subdominant, `bVII7`/`bVI7`→minor subdominant `Emp`, `II7`→altered subdominant) are cited
facts, NOT curation suspects: the tritone curation ledger (baseline and persistence view)
SHALL exempt them, so the residual ledger contains only genuinely unadjudicated readings.

#### Scenario: bVII7 is a minor subdominant, not a secondary dominant
- **WHEN** in C major the chord `Bb7` resolves up a whole step to `C`
- **THEN** it is classified as a minor-subdominant / modal-interchange chord (`bVII7`)
- **AND** it is NOT labeled a secondary dominant

#### Scenario: bVII7 with a diatonic fourth-up resolution is a secondary dominant
- **WHEN** in A minor the chord `G7` (bVII7) resolves to `C` (the diatonic third degree)
- **THEN** it is classified `Dsec` (`V7/III`), not `Emp` — resolution precedes borrowing

#### Scenario: Blues sevenths on I and IV are not secondary dominants
- **WHEN** in C major `C7` (`I7`) and `F7` (`IV7`) appear in a blues context
- **THEN** each is classified as a blues chord, not a secondary dominant

#### Scenario: VII7 resolving to the tonic is cadential
- **WHEN** in C major a long `B7` resolves directly to `C` and is not preceded by a ii cadential
- **THEN** it is classified as a cadential `VII7`
- **AND** a short `B7` in the `F#m7 B7` cliché is classified as `V7/III` instead

#### Scenario: VII7 without tonic resolution reads as V7/III
- **WHEN** in C major a `B7` is followed by neither `C` nor its diatonic target
- **THEN** it is classified `Dsec` with expected target `(V7/III)` (p.112(2), deceptive p.114)

#### Scenario: II7 is an altered subdominant
- **WHEN** in C major a `D7` matches no dominant branch (e.g. followed by `C7M`)
- **THEN** it is classified `SD` as "Subdominante alterada (II7)" (quadro p.113)

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

#### Scenario: Documented special functions are exempt from the curation ledger
- **WHEN** the tritone curation ledger is computed (baseline or persistence view)
- **THEN** occurrences reading as blues `I7` (`T`, degree I), blues `IV7` (`SD`, degree IV),
  minor subdominant (`Emp`), or altered subdominant `II7` (`SD`, degree II) are exempt with
  their citation (quadro p.113)
- **AND** the residual ledger contains only unadjudicated readings
