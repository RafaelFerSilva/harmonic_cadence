## 1. Modal tonal center (`harmonic_analysis/domain/modal.py`)

- [x] 1.1 Classify mode from diatonic pitch-class collection + tonic (reuse `theory.MODE_PATTERNS`)
- [x] 1.2 Require modal evidence (no leading tone + characteristic degree) with a conservative threshold; default tonal
- [x] 1.3 Modal degrees relative to the modal tonic; characteristic-chord identification
- [x] 1.4 Modal cadences: bVII–I (mixolydian), bII–I (phrygian), v–i / IV–i shapes
- [x] 1.5 Expose mode on `KeyEstimate` (key-detection delta)
- [x] 1.6 Tests: mixolydian (G F C G), dorian (Dm G Dm Em), tonal stays major/minor; bVII not Emp; modal cadences

## 2. Roman numeral analysis (`harmonic_analysis/domain/roman.py`)

- [x] 2.1 Numeral with degree + quality (case, °, +, seventh suffix)
- [x] 2.2 Inversion figures from `Chord.bass` position (6, 6/4, 6/5, 4/3, 4/2; none for root)
- [x] 2.3 Applied-chord notation (V7/x, vii°/x) consistent with applied-dominant-analysis
- [x] 2.4 Integrate into `HarmonicAnalysis`; add `roman_numerals` to the result
- [x] 2.5 Tests: diatonic triads I..vii°; G7=V7, Cmaj7=Imaj7; C/E=I6; C/G=I6/4; G7/B=V6/5; E7→Am=V7/vi

## 3. Voice-leading analysis (`harmonic_analysis/domain/voice_leading.py`)

- [x] 3.1 Bass line extraction (slash bass, else root) + motion in semitones
- [x] 3.2 Descending bass detection, diatonic vs chromatic
- [x] 3.3 Pedal-point detection (sustained bass across changing chords)
- [x] 3.4 Line-cliché detection (static root, chromatic inner motion)
- [x] 3.5 Integrate into `HarmonicAnalysis`; add `voice_leading` to the result
- [x] 3.6 Tests: C/E bass=E; Dm Dm/C# Dm/C Dm/B chromatic descent; C G/B Am Am/G descent; G pedal; Cm cliché

## 4. Chord-scale & tensions (`harmonic_analysis/domain/chord_scale.py`)

- [x] 4.1 Function/degree → recommended chord-scale table (Ionian/Dorian/Mixolydian/Locrian/…)
- [x] 4.2 Available tensions (whole step above a chord tone) + avoid notes (semitone above a chord tone)
- [x] 4.3 Integrate into `HarmonicAnalysis`; add `chord_scales` to the result
- [x] 4.4 Tests: Imaj7→Ionian w/ 9,13 + ♮11 avoid; iim7→Dorian w/ 9,11,13; V7→Mixolydian; iiø7→Locrian

## 5. Wire-up & report

- [x] 5.1 `AnalysisService` populates `modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`
- [x] 5.2 `Emp` no longer marks chords diatonic to an active mode
- [x] 5.3 Preserve existing report sections and `HarmonicAnalysis` public signatures
- [x] 5.4 Integration test over a song exercising all four new sections

## 6. Validation & verification

- [x] 6.1 Extend the validation corpus (modal pieces, inversions, descending bass, tensions)
- [x] 6.2 Full suite green across all packages
- [x] 6.3 Real-cifra spot check (in-process): modal/RNA/voice-leading/tensions populated, no regression
