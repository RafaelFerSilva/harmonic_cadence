## Context

The analyzer reasons over chord **symbol strings** (`root` + boolean quality flags), with no pitch-class/interval model. Two consequences block accuracy:

- `NOTE_REPLACEMENTS` collapses flats to sharps (`Db→C#`), erasing spelling that functional analysis depends on.
- `guess_key` (first chord / minor ratio) and a single fixed key for the whole piece; applied-dominant detection uses inverted intervals.

This change adds the theory foundation and corrects key/applied-dominant analysis. Repertoire is Brazilian popular music (bossa, choro, samba, forró, MPB), which is heavily seventh-chord and tritone-sub oriented — spelling and applied dominants matter a lot.

## Goals / Non-Goals

**Goals:**
- A spelling-preserving pitch/interval/chord-realization core in `cifra_core`.
- Krumhansl-Schmuckler key detection from chords, with modulation segmentation.
- Correct secondary-dominant and tritone-substitute detection.
- A small annotated validation corpus with an accuracy metric to lock regressions.

**Non-Goals (later tiers):** modes as first-class tonal centers, Roman numerals with inversions, voice-leading/bass-line analysis, chord-scale/tensions, reharmonization, probabilistic functional parsing.

## Decisions

### D1 — Own lightweight theory core over `music21`
Build `cifra_core/theory/` (pitch, realization, scales) rather than depend on `music21`.
- **Why:** keeps the in-process provider light, avoids a heavy academic dependency, and lets us tune for Brazilian cifra notation (`7M`, `°`, slash bass). We mirror `music21`'s concepts (Pitch, interval, chord) without the footprint.
- **Alternative:** integrate `music21` — rejected for weight and Brazilian-notation friction; revisit only if scope grows.

### D2 — Note = (letter, accidental) → derived pitch class
A `Note` stores letter `A–G` and accidental (double-flat … double-sharp); pitch class is derived. Equality is by (letter, accidental); pitch class is a separate accessor. Spelling within a key uses the key signature / circle of fifths.
- **Why:** preserves `bII` vs `#I`; enables correct diatonic spelling (one letter per scale degree).

### D3 — Chord realization is key-independent; spelling comes later
Realize a chord symbol into a **pitch-class set** via interval recipes per quality (e.g. `maj7 = {0,4,7,11}`, `m7b5 = {0,3,6,10}`), independent of any key. Spelling (choosing letters/accidentals) happens **after** the key is known.
- **Why:** key detection needs pitch classes before a key exists; spelling is a key-dependent presentation step. Avoids a chicken-and-egg between spelling and key.

### D4 — Krumhansl-Schmuckler over a chord-derived profile
Build a 12-bin profile by accumulating realized chord pitch classes (root-weighted), then correlate against the 24 K-S major/minor profiles; return ranked keys with scores.
- **Why:** standard, well-understood, deterministic; far more robust than first-chord. Root weighting compensates for having chords (not a melody/durations).
- **Cadential weighting:** the final chord's root receives extra weight (resolution tends to the tonic). This made detection independent of the *first* chord while lifting corpus accuracy to 100% (notably fixing ii-V-I read as the dominant key). It does mean ordering matters at the *cadence* — a deliberate, musically-grounded trade-off (key-finding is not order-invariant; pieces resolve to their tonic).
- **Alternative:** purely diatonic-fit counting — rejected as weaker on chromatic repertoire.

### D5 — Modulation by windowed detection with hysteresis
Slide a window over the chord sequence, run K-S per window, then merge adjacent same-key windows into regions; apply a minimum-region length / hysteresis to avoid flapping on a single borrowed chord.
- **Why:** Brazilian repertoire modulates; one key per piece is wrong. Hysteresis prevents over-segmentation.

### D6 — Reimplement applied dominants on correct intervals
`V7/x`: dominant-7 whose target root is a perfect fourth above (5 semitones), i.e. resolution down a perfect fifth. `SubV` (`bII7`): dominant-7 a semitone above the target, resolving down a semitone. Replaces the current `==7` (secondary) and `==1` (SubV) checks.
- **Why:** the current checks are inverted (see proposal Impact); the new model + intervals make the correct relationship explicit and testable.

### D7 — Validation corpus + accuracy metric
A fixture of annotated `(artist, song, key)` plus synthetic progressions with known keys; a test computes key-detection accuracy and fails below a threshold.
- **Why:** "state of the art" requires measurement; the metric guards against regressions as later tiers land.

## Risks / Trade-offs

- **Spelling edge cases (double accidentals, rare keys)** → scope to common keys/qualities first; cover with tests; degrade gracefully to pitch class when unsure.
- **K-S on chords (no durations) is approximate** → root-weight the profile and validate/tune on the corpus; expose confidence so callers can see ambiguity.
- **Modulation over-segmentation** → minimum-region length + hysteresis; default conservative.
- **Enharmonic change ripples into degree/function/reports** → keep `HarmonicAnalysis` public methods stable; cover the degree→function→report path with integration tests.
- **Chicken-and-egg (spelling vs key)** → resolved by D3 (realize in pitch classes, spell after key).

## Migration Plan

1. Build `cifra_core/theory/` (pitch, interval, realization, scales) with no behavior change to existing code.
2. Add `key_detection.py` (profile, K-S, modulation) in `harmonic_analysis/domain`.
3. Switch `HarmonicAnalysis` internals (degree/interval) onto the theory core; preserve public method signatures; retire the `Db→C#` collapse for analysis.
4. Reimplement `Dsec`/`SubV` in `analyze_function` on correct intervals.
5. Add the validation corpus + accuracy test; tune weighting/thresholds.
6. Verify the report path (degree/function/cadence/progression) is unchanged except for the corrections.

## Open Questions

- Profile weighting: roots only, all chord tones, or extra bass/cadential emphasis?
- Keep `guess_key` as a deprecated shim, or remove and update callers?
- Minimum region length / hysteresis threshold for modulation?
- Default spelling policy for chords analyzed outside any detected key region?
