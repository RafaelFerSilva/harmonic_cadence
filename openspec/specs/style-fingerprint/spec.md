# style-fingerprint Specification

## Purpose

The analyzer aggregates harmonic features across a set of analyzed songs into a style fingerprint and compares two fingerprints with a similarity/distance measure, so artists or corpora can be contrasted.

## Requirements

### Requirement: Harmonic style fingerprint

The analyzer SHALL aggregate harmonic features across a set of analyzed songs into a style fingerprint, including at least: the harmonic-function distribution, the function-to-function transition matrix, cadence-type counts, modal usage, and a tension-density summary.

#### Scenario: Function distribution is a normalized profile
- **WHEN** a fingerprint is built from one or more analyses
- **THEN** the function distribution weights sum to 1 (a probability profile)
- **AND** every function that occurs has a non-zero weight

#### Scenario: Fingerprint carries the expected sections
- **WHEN** a fingerprint is produced
- **THEN** it includes the function distribution, the transition matrix, cadence counts, modal usage, and a tension-density value

### Requirement: Fingerprint comparison

The analyzer SHALL compare two fingerprints with a similarity/distance measure, so two artists/corpora can be contrasted.

#### Scenario: Identical corpora are maximally similar
- **WHEN** a fingerprint is compared with itself
- **THEN** the similarity is maximal (distance zero)

#### Scenario: Different corpora differ
- **WHEN** two clearly different corpora (e.g. a diatonic-pop set vs a chromatic-jazz set) are compared
- **THEN** the similarity is lower than the self-comparison
