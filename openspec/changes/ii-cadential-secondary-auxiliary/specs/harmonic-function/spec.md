## ADDED Requirements

### Requirement: II cadential chord classified by its dominant's target

The analyzer SHALL recognize a **II cadential** chord (Chediak Vol. I, XIX, p.100): a **minor** chord separated from a dominant by an ascending perfect fourth (the dominant root five semitones above the minor chord's root), i.e. the `IIm` of a `IIm V7 → x` cadence. It SHALL classify the II cadential by the **target of that dominant** — the chord a perfect fifth below the dominant's root, `target = (dominant_root + 5) mod 12`:

- **Primary**: the dominant resolves to the **tonic** (`Dm7 G7 → C`).
- **Secondary**: the dominant resolves to a **diatonic degree** other than the tonic (`F#m7 B7 → Em`, the ii-V of the third degree).
- **Auxiliary**: the dominant resolves to a **modal-interchange (borrowed) chord** — a non-diatonic target (`Cm7 F7 → Bb`, the ii-V of bVII).

The II cadential reading SHALL take precedence over labeling the minor chord by its plain diatonic function (`SD`) or — for the chromatic secondary/auxiliary cases — as a modal borrowing (`Emp`) or tonic (`T`). The classification mirrors the applied-dominant axis (secondary = diatonic target, auxiliary = borrowed target). Because chord sheets carry no metre, the detection uses the harmonic relation (minor chord followed by a dominant a perfect fourth above), not Chediak's strong-beat criterion.

#### Scenario: Primary II cadential (ii-V-I)
- **WHEN** in C major `Dm7` is followed by `G7` whose target a fifth below is `C` (the tonic)
- **THEN** `Dm7` is classified as a primary II cadential

#### Scenario: Secondary II cadential preparing a diatonic degree
- **WHEN** in C major `F#m7` is followed by `B7` whose target a fifth below is `E` (the diatonic third degree)
- **THEN** `F#m7` is classified as a secondary II cadential (of `V7/III`)
- **AND** it is NOT labeled a modal borrowing (`Emp`)

#### Scenario: Secondary II cadential preparing the dominant degree
- **WHEN** in C major `Am7` is followed by `D7` whose target a fifth below is `G` (the diatonic fifth degree)
- **THEN** `Am7` is classified as a secondary II cadential (of `V7/V`)
- **AND** it is NOT labeled tonic (`T`)

#### Scenario: Auxiliary II cadential preparing a borrowed chord
- **WHEN** in C major `Cm7` is followed by `F7` whose target a fifth below is `Bb` (a bVII borrowed chord)
- **THEN** `Cm7` is classified as an auxiliary II cadential (of `V7/bVII`)
- **AND** it is NOT labeled tonic (`T`) or modal borrowing (`Emp`)

#### Scenario: A minor chord not followed by a fourth-above dominant is not a II cadential
- **WHEN** a minor chord is not followed by a dominant-seventh a perfect fourth above its root
- **THEN** it is NOT classified as a II cadential and keeps its ordinary functional reading
