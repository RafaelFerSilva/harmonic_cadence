# key-accuracy-evaluation Specification

## Purpose
TBD - created by archiving change validation-harness. Update Purpose after archive.
## Requirements
### Requirement: Key-detection accuracy harness

The project SHALL provide a harness that evaluates key-detection accuracy against annotated keys. Given a corpus of `(name, chords, annotated_key)`, it SHALL report three metrics: **mode accuracy** (major/minor), **exact accuracy** (tonic and mode), and **relative-aware accuracy** (counting a detection that differs from the annotation only by the relative major/minor as a near-match). An annotated key is parsed from a label where a trailing `m` denotes minor (e.g. `"G"` = G major, `"Am"` = A minor).

#### Scenario: An exact detection counts toward all metrics
- **WHEN** the detected key equals the annotated key (same tonic and mode)
- **THEN** the song counts toward mode, exact, and relative-aware accuracy

#### Scenario: A relative-only difference is a near-match
- **WHEN** the annotation is C major and the detection is A minor (its relative)
- **THEN** the song counts toward relative-aware accuracy
- **AND** it does NOT count toward exact accuracy

#### Scenario: Relative-aware accuracy is never below exact accuracy
- **WHEN** a corpus is evaluated
- **THEN** the relative-aware accuracy is greater than or equal to the exact accuracy

#### Scenario: Only annotated songs are evaluated
- **WHEN** the corpus is loaded from a directory
- **THEN** songs without an annotated key are excluded from the evaluation

