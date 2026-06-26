## 1. Theory core (`cifra_core/theory/`)

- [x] 1.1 `Note` model: letter + accidental, derived pitch class; parse/render; `Db` ≠ `C#`, same pc
- [x] 1.2 `Interval`: ascending semitone distance between notes (+ magnitude helper)
- [x] 1.3 Chord realization: symbol → key-independent pitch-class set via per-quality recipes (maj7, m7, 7, m7b5, dim7, 6, 9/11/13, 7M, °, sus)
- [x] 1.4 Scales/modes from a tonic with correct diatonic spelling (church modes + harmonic/melodic minor)
- [x] 1.5 Export the theory API from `cifra_core`
- [x] 1.6 Tests: spelling distinctness, intervals (E→A = 5, tritone = 6), realization (Cmaj7, Dm7b5, C7M), scale spelling (F major Bb; G mixolydian F natural)

## 2. Key detection (`harmonic_analysis/domain/key_detection.py`)

- [x] 2.1 Pitch-class profile builder from a chord sequence (root-weighted)
- [x] 2.2 Krumhansl-Schmuckler correlation vs the 24 major/minor profiles → ranked keys + scores
- [x] 2.3 Single-key estimate API returning chosen key, score, and runner-up
- [x] 2.4 Modulation segmentation: windowed K-S + merge into regions with hysteresis/min-length
- [x] 2.5 Tests: C-major progression → C major; order-independence; relative major/minor near-tie; multi-region vs single-region

## 3. Applied dominants (correctness fixes)

- [x] 3.1 Secondary dominant `V7/x` via descending-fifth resolution (target a perfect fourth / 5 semitones above)
- [x] 3.2 Tritone substitute `SubV` (bII7) via root a semitone above the target
- [x] 3.3 Tests: `E7→Am` = V7/vi; `D7→G` = V7/V; `Db7→C` = SubV; inverted relationships rejected

## 4. Wire into `HarmonicAnalysis`

- [x] 4.1 Switch degree/interval computation onto the theory core; stop using `Db→C#` collapse for analysis
- [x] 4.2 Replace `guess_key` with key detection; expose tonal regions to the analysis result
- [x] 4.3 Reimplement `Dsec`/`SubV` branches of `analyze_function` per group 3
- [x] 4.4 Preserve public method signatures of `HarmonicAnalysis`; keep report shape stable
- [x] 4.5 Integration test: degree → function → cadence → progression path over a known song

## 5. Validation corpus + metric

- [x] 5.1 Annotated fixture: `(artist, song, key)` + synthetic progressions with known keys
- [x] 5.2 Accuracy test for key detection with a threshold gate
- [x] 5.3 Tune profile weighting / modulation thresholds against the corpus; record the chosen values

## 6. Verification

- [x] 6.1 Full suite green across all packages
- [x] 6.2 Spot-check a real cifra end-to-end (in-process) and confirm key/applied-dominant improvements vs. before
- [x] 6.3 Confirm no regression in the existing report sections (cadences, progressions, function stats)
