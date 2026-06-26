# voice-leading-analysis Specification

## Purpose

The analyzer derives the bass line from each chord and characterizes its motion, detecting descending bass lines (diatonic vs. chromatic), pedal points, and static-harmony line clichés.

## Requirements

### Requirement: Bass line extraction and motion

The analyzer SHALL derive the bass line from each chord (its slash bass when present, otherwise its root) and describe the motion between successive bass notes (stepwise, leap, repeated) in semitones.

#### Scenario: Bass uses the slash note when present
- **WHEN** the chord `C/E` is analyzed
- **THEN** its bass is `E` (not the root `C`)

#### Scenario: Motion between bass notes is reported
- **WHEN** consecutive chords have bass notes `C` then `D`
- **THEN** the bass motion is reported as ascending by two semitones (stepwise)

### Requirement: Descending bass line detection

The analyzer SHALL detect descending bass lines, distinguishing diatonic from chromatic, over consecutive chords.

#### Scenario: Chromatic descending bass (line cliché)
- **WHEN** the progression `Dm  Dm/C#  Dm/C  Dm/B` is analyzed
- **THEN** a descending chromatic bass line is reported spanning those chords

#### Scenario: Diatonic descending bass
- **WHEN** the progression `C  G/B  Am  Am/G` is analyzed
- **THEN** a descending bass line is reported

### Requirement: Pedal point detection

The analyzer SHALL detect a pedal point: a sustained bass note held across two or more changing chords.

#### Scenario: Tonic pedal
- **WHEN** the progression `C/G  F/G  G  C/G` keeps `G` in the bass across changing chords
- **THEN** a pedal point on `G` is reported

### Requirement: Static-harmony line cliché

The analyzer SHALL detect a line cliché: a chromatically moving voice over an otherwise static chord (e.g. the descending major-third/seventh line on a minor chord).

#### Scenario: Minor line cliché
- **WHEN** the progression `Cm  Cm(maj7)  Cm7  Cm6` is analyzed
- **THEN** a line cliché over the static `Cm` harmony is reported
