## ADDED Requirements

### Requirement: Emission weighted by functional strength

The HMM emission for a chord SHALL be weighted by the functional strength of its diatonic degree (Chediak, p. 92): a strong-function degree (I, IV, V) concentrates more emission mass on the deterministic label, a weak-function degree (III, VI) spreads more mass to the alternatives, and a medium degree (II, VII) sits between. A chord with no diatonic strength keeps the default emission, and a parse driven only by function codes (no strength provided) MUST behave identically to the unweighted model. The weighting MUST preserve determinism.

#### Scenario: A strong-function chord is more confident than a weak-function one
- **WHEN** the progression `C Am Dm G7` in C major is parsed with functional strength
- **THEN** the strong-degree dominant `G7` (V) has higher chosen-function confidence than the weak-degree `Am` (vi)

#### Scenario: A weak-function chord still lists alternatives
- **WHEN** a weak-degree chord (e.g. `Am` = vi in C major) is parsed
- **THEN** it reports its chosen function with a confidence and at least one alternative with a probability

#### Scenario: A code-only parse is unchanged
- **WHEN** a progression is parsed from function codes alone, without any functional strength
- **THEN** the functional path, the per-chord confidences, and the alternatives equal those of the unweighted model

#### Scenario: The weighted parse is deterministic
- **WHEN** the same progression is parsed twice with strength weighting
- **THEN** the path, confidences, and alternatives are identical both times
