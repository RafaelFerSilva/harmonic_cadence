## ADDED Requirements

### Requirement: Most-probable functional path via Viterbi

The analyzer SHALL compute the most probable sequence of harmonic functions for a chord progression using a hidden Markov model (states = harmonic functions; emissions = chord→function likelihoods; transitions = a functional grammar) decoded with the Viterbi algorithm. This MUST complement, not replace, the existing deterministic function analysis.

#### Scenario: A clear cycle yields the expected functional path
- **WHEN** the progression `C F G7 C` (T–SD–D–T) is parsed
- **THEN** the most probable functional path is `[T, SD, D, T]`

#### Scenario: The path respects functional grammar
- **WHEN** any progression is parsed
- **THEN** the decoded path maximizes the product of emission and transition probabilities
- **AND** a dominant resolving to the tonic is scored as a likely transition

### Requirement: Per-chord confidence and alternative parses

The functional parse SHALL expose a confidence for each chord's chosen function and at least one alternative function with its probability when the chord is ambiguous.

#### Scenario: Ambiguous chord reports alternatives
- **WHEN** a chord admits more than one plausible function (e.g. a vi chord readable as tonic substitute or as a ii in another region)
- **THEN** the result reports the chosen function with a confidence
- **AND** lists at least one alternative function with a probability

#### Scenario: Unambiguous chord has high confidence
- **WHEN** a chord has a single dominant interpretation in context (e.g. `G7` resolving to `C` in C major)
- **THEN** its chosen-function confidence is high relative to its alternatives

#### Scenario: The parse is deterministic
- **WHEN** the same progression is parsed twice
- **THEN** the functional path, the per-chord confidences, and the alternatives are identical both times
