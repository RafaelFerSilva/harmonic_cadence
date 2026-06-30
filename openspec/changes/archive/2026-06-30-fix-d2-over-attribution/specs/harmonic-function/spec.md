## MODIFIED Requirements

### Requirement: II cadential chord classified by its dominant's target

The analyzer SHALL recognize a **II cadential** chord (Chediak Vol. I, XIX, p.100): a **minor** chord separated from a dominant by an ascending perfect fourth (the dominant root five semitones above the minor chord's root), i.e. the `IIm` of a `IIm V7 → x` cadence. **The following dominant MUST actually RESOLVE to its target** — a II cadential prepares a dominant *function*, and a dominant functions only when it resolves down a perfect fifth to its target chord. Concretely, with the dominant at index `i+1` and `target = (dominant_root + 5) mod 12`, the chord at index `i+2` MUST have its root (or bass) equal to `target`; otherwise the dominant does not function as a dominant (it is a non-resolving blues `I7`/`IV7` or a non-resolving borrowed chord) and the preceding minor chord is **not** a II cadential — it keeps its ordinary functional reading. This resolution test is purely intervallic (transposition-invariant) and does not depend on the dominant's own function code, which the blues-position branch may color as `T`/`SD` before resolution is considered. When the precondition holds, the analyzer SHALL classify the II cadential by the **target of that dominant**:

- **Primary**: the dominant resolves to the **tonic** (`Dm7 G7 → C`).
- **Secondary**: the dominant resolves to a **diatonic degree** other than the tonic (`F#m7 B7 → Em`, the ii-V of the third degree). The target MAY itself be a dominant chain link (`Em7 A7 → D7`); the dominant still functions because it resolves down a fifth.
- **Auxiliary**: the dominant resolves to a **modal-interchange (borrowed) chord** — a non-diatonic target (`Cm7 F7 → Bb`, the ii-V of bVII).

The II cadential reading SHALL take precedence over labeling the minor chord by its plain diatonic function (`SD`) or — for the chromatic secondary/auxiliary cases — as a modal borrowing (`Emp`) or tonic (`T`). The classification mirrors the applied-dominant axis (secondary = diatonic target, auxiliary = borrowed target). Because chord sheets carry no metre, the detection uses the harmonic relation (minor chord followed by a dominant a perfect fourth above that resolves to its target), not Chediak's strong-beat criterion.

#### Scenario: Primary II cadential (ii-V-I)
- **WHEN** in C major `Dm7` is followed by `G7` whose target a fifth below is `C` (the tonic), and the chord after `G7` resolves to `C`
- **THEN** `Dm7` is classified as a primary II cadential

#### Scenario: Secondary II cadential preparing a diatonic degree
- **WHEN** in C major `F#m7` is followed by `B7` whose target a fifth below is `E`, and the chord after `B7` resolves to `E`
- **THEN** `F#m7` is classified as a secondary II cadential (of `V7/III`)
- **AND** it is NOT labeled a modal borrowing (`Emp`)

#### Scenario: Secondary II cadential whose dominant resolves into another dominant
- **WHEN** `Em7` is followed by `A7` and the chord after `A7` is `D7` (root `D` = `A7`'s target), continuing a dominant chain
- **THEN** `Em7` is classified as a secondary II cadential (the `A7` functions as a dominant because it resolves down a fifth)

#### Scenario: Auxiliary II cadential preparing a borrowed chord
- **WHEN** in C major `Cm7` is followed by `F7` whose target a fifth below is `Bb`, and the chord after `F7` resolves to `Bb`
- **THEN** `Cm7` is classified as an auxiliary II cadential (of `V7/bVII`)
- **AND** it is NOT labeled tonic (`T`) or modal borrowing (`Emp`)

#### Scenario: A minor chord before a non-resolving dominant is not a II cadential
- **WHEN** `Dm7` is followed by `G7` (a fourth above) but the chord after `G7` is not `G7`'s target `C` (e.g. it loops back to `Dm7`, as when `G7` is a static blues `I7`)
- **THEN** `Dm7` is NOT classified as a II cadential (its dominant does not resolve, so it does not function as a dominant)
- **AND** `Dm7` keeps its ordinary functional reading

#### Scenario: A minor chord not followed by a fourth-above dominant is not a II cadential
- **WHEN** a minor chord is not followed by a dominant-seventh a perfect fourth above its root
- **THEN** it is NOT classified as a II cadential and keeps its ordinary functional reading
