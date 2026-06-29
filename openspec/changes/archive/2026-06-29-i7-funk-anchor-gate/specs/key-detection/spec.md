## ADDED Requirements

### Requirement: Anchor gate recovers an I7-funk center detected as its IV

The analyzer SHALL correct the Krumhansl-Schmuckler center estimate `Y` to a candidate `X`
when a song has an **I7-funk** center (Chediak XXXIV: the seventh over the tonic is a special
blues/funk function, not a dominant) that K-S mistakes for its subdominant. This is the
**inverse geometry** of the functional-dominant quality gate: there the engine picks the V and
corrects down a fifth; here the funk tonic `X` is voiced as a dominant-seventh (`I7`), its IV
(`Y = (X + 5) mod 12`) is more frequent and rests, so K-S picks the IV, and the correction is
to a center a fifth **above** the guess. Because the funk tonic offers no V→I cadence and loses
on frequency, the recovering signal is **structural** (the piece opens and closes on `X`), not
statistical or cadential.

The correction SHALL be ultraconservative — firing only when ALL of the following hold, each
encoding a property of the I7-funk pattern:

1. the first and last chords share root `X` (the piece opens and closes "at home");
2. the K-S winner `Y` is the IV of `X` (`Y == (X + 5) mod 12`, `X != Y`);
3. `X` appears as a dominant-seventh somewhere (the tonic sounds like a dominant — `I7` funk);
4. `X` also appears as a plain major triad somewhere (it genuinely rests — distinguishing a
   funk tonic from a mere V pedal, where `X` would appear only as `X7`);
5. `X` is among the top-2 K-S alternatives (not a wild flip).

This path SHALL be geometrically separate from the V-as-tonic gate (which corrects down a
fifth, anchored on functional resolution) and SHALL NOT alter the K-S correlation or the
cadential-corroboration stage.

#### Scenario: An I7-funk tonic detected as its IV is recovered
- **WHEN** a song opens and closes on `E`, `E` appears both as `E7` and as a plain `E` triad, and K-S picks `A` (the IV of `E`, with `E` as a top-2 alternative)
- **THEN** the detected center is corrected to `E`

#### Scenario: A confident non-funk key is untouched
- **WHEN** the piece does not open and close on the same root, or the K-S winner is not the IV of that root
- **THEN** the anchor gate does not fire and the K-S center stands

#### Scenario: A pure V pedal is not mistaken for an I7-funk tonic
- **WHEN** a song opens and closes on `X` but `X` appears only as a dominant-seventh (never as a resting major triad)
- **THEN** the anchor gate does not fire (guard 4 fails) and the K-S center stands
