## MODIFIED Requirements

### Requirement: The five harmonic cadences

The analyzer SHALL classify harmonic cadences into Chediak's five types (Vol. I, pp. 109-111): **perfect** (V→I in root position), **imperfect** (V→I with an inversion, or VII→I), **plagal** (IV→I or iim→I), **half** (any degree → V), and **deceptive** (V → any degree that is not the tonic). It SHALL additionally recognize the **authentic** cadence — a perfect cadence preceded by a subdominant (IV or ii → V → I). Classification is by scale-degree position, so it applies in both major and minor.

A cadence is, in Chediak's terms, a **combination of harmonic functions** (Vol. I, XXXII, p.110 — *"a cadência imperfeita é o resultado da combinação 'D' e 'T'"*), not a mere sequence of scale degrees. Therefore, for any cadence that **resolves to the tonic** (perfect, imperfect, plagal, and the authentic three-chord form), when the per-chord **function codes** are available, the target chord MUST FUNCTION as a repose (tonic) chord. If the target — though spelled on the tonic degree — carries a **non-repose function** assigned by the function coder (a dominant family code `D`/`D2`/`Dsec`/`Daux`/`Dext`, a tritone-substitute `SubV`/`Sub2`, or a diminished `Dim`), the V→I (or IV/ii→I) motion is **NOT a cadence**: it is a **direct resolution** (Chediak XXXIII, p.111 — a dominant resolving into a chord that is itself a `ii` of a tonicization is a chain link, e.g. `Em7 A7 → Dm7`), and the analyzer SHALL NOT report it as a perfect, imperfect, plagal, or authentic cadence. Such a pair is **suppressed** (not reclassified as deceptive — a deceptive cadence is a phrase-punctuation event; a chain link is not). When function codes are not provided, classification falls back to scale-degree position (backward compatible). The half cadence (rest on V) and the deceptive cadence (V → a non-tonic) do not resolve to the tonic and are unaffected by this function guard.

#### Scenario: Perfect cadence is root-position V–I
- **WHEN** the progression `G7 C` (V→I) occurs with both chords in root position in C major
- **THEN** a perfect cadence is reported for `G7 → C`

#### Scenario: An inverted V–I is imperfect, not perfect
- **WHEN** `G7 C/E` (V→I with the tonic inverted) occurs in C major
- **THEN** an imperfect cadence is reported
- **AND** it is NOT reported as a perfect cadence

#### Scenario: VII–I is an imperfect cadence
- **WHEN** `Bm7b5 C` (vii→I) occurs in C major
- **THEN** an imperfect cadence is reported

#### Scenario: Plagal includes the ii–I shape
- **WHEN** `F C` (IV→I) or `Dm C` (ii→I) occurs in C major
- **THEN** a plagal cadence is reported for each

#### Scenario: Deceptive is V to any non-tonic
- **WHEN** `G7 Am` (V→vi) or `G7 F` (V→IV) occurs in C major
- **THEN** a deceptive cadence is reported for each

#### Scenario: Half cadence rests on the dominant
- **WHEN** `Dm G` (ii→V) occurs in C major
- **THEN** a half cadence is reported

#### Scenario: Authentic cadence is a prepared perfect cadence
- **WHEN** `Dm7 G7 C` (ii→V→I) occurs in C major
- **THEN** an authentic cadence is reported for the three-chord progression

#### Scenario: A V→I whose target functions as a dominant is not a cadence
- **WHEN** `B7 Em7` is a V→I by scale degree but the function coder assigns `Em7` a `D2` (ii-cadential) function — because `Em7` launches a `Em7 A7 → D` tonicization (Chediak XXXIII direct resolution)
- **THEN** the pair is NOT reported as a perfect, imperfect, or authentic cadence
- **AND** it is NOT reported as a deceptive cadence (it is a chain link, suppressed)

#### Scenario: A V→I whose target functions as a diminished chord is not a cadence
- **WHEN** `E7 A°` is a V→I by scale degree but the function coder assigns `A°` a `Dim` (auxiliary/passing diminished) function
- **THEN** the pair is NOT reported as a perfect, imperfect, or authentic cadence

#### Scenario: A V→I whose target functions as the tonic is a cadence (regression)
- **WHEN** `G7 C` is a V→I and the function coder assigns `C` a tonic (`T`) function
- **THEN** a perfect cadence is reported as usual (the function guard only suppresses non-repose targets)

#### Scenario: Without function codes, classification is by degree (backward compatible)
- **WHEN** `analyze_cadences` is called with no per-chord function codes
- **THEN** cadences are classified by scale-degree position exactly as before
