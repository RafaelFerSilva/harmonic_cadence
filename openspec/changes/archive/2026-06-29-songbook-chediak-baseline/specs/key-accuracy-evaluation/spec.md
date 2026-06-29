## REMOVED Requirements

### Requirement: Key-detection accuracy harness

**Reason**: The harness scored `detect_key` against the Cifra Club annotation (mode / exact-tonic /
relative-aware / collection vs `cc_key`). The team retired the Cifra Club as a base of validation —
it is now a cifra *source* only. These metrics measured fidelity to a crowd-sourced annotation,
not to Chediak's theory, contradicting the project's Golden Rule.

**Migration**: Quality is now measured by `functional-analysis-baseline` — agreement of `detect_key`
with the **Chediak-functional center** (the functional-dominant criterion read from the music) and
the **Chediak functional invariants**, over the local songbook corpus, transposition-invariant.

### Requirement: Real-song baseline uses the source's own key as independent gold

**Reason**: This requirement made the Cifra Club's own `key` the gold (anti-transposition exact
tonic). With the Cifra Club demoted to a source, its annotation is no longer gold for anything.

**Migration**: The baseline corpus is the local songbook (`cifras/*.md`, via the local-chord-input
path); the center gold is the Chediak-functional criterion, not the source annotation. See
`functional-analysis-baseline`.

### Requirement: Baseline documents expected accuracy after each calibration change

**Reason**: The documented numbers were the four `cc_key`-anchored metrics; with those retired,
the "expected accuracy after calibration" framed against `cc_key` no longer applies.

**Migration**: Each calibration is now measured against the functional-center coverage/agreement
and the functional-invariant pass rate over the songbook (`functional-analysis-baseline`); those
numbers are the new zero-regression reference.

### Requirement: Structural center gold and transposition-invariant center accuracy

**Reason**: The center metric was computed as an offset relative to `cc_key`
(`(detected − cc_key) % 12 == structural_offset`), with a `verified` tier confirming `cc_key` and a
`chediak`-tonal tier curated against `cc_key`. All of it is anchored on the Cifra Club annotation,
which is no longer a base.

**Migration**: The tonal center is established by Chediak's functional-dominant criterion read from
the music (no annotation), and `detect_key` is scored for agreement with it — see "Tonal center is
established by Chediak's functional criterion" in `functional-analysis-baseline`. The
`chediak`-tonal `cc_key`-anchored tier is dropped.

### Requirement: Baseline reports tonal center accuracy and the center hole

**Reason**: This reported the `cc_key`-anchored center accuracy + hole, retired with the metric
above.

**Migration**: The baseline now reports functional-center **coverage + agreement + hole** over the
songbook, grounded in the Chediak-functional center (`functional-analysis-baseline`).
