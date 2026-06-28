## MODIFIED Requirements

### Requirement: Key-detection accuracy harness

The project SHALL provide a harness that evaluates key-detection accuracy against annotated keys. Given a corpus of `(name, chords, annotated_key)`, it SHALL report four metrics: **mode accuracy** (major/minor), **exact accuracy** (tonic and mode), **relative-aware accuracy** (counting a detection that differs from the annotation only by the relative major/minor as a near-match), and **collection accuracy** (counting a detection whose tonic is a diatonic degree of the annotated key's scale — i.e. the correct diatonic collection / key signature — even when the tonal center within it is wrong). An annotated key is parsed from a label where a trailing `m` denotes minor (e.g. `"G"` = G major, `"Am"` = A minor).

Collection accuracy is computed by `same_collection(gold, detected)`: `True` when `(detected_tonic_pc - gold_tonic_pc) % 12` is a member of the gold's diatonic offset set (major `{0,2,4,5,7,9,11}`, minor natural `{0,2,3,5,7,8,10}`). It ignores the detected major/minor label, because that label is unreliable for modal pieces (e.g. K-S reports "E minor" for an E-Phrygian piece whose collection is C major's).

#### Scenario: An exact detection counts toward all metrics
- **WHEN** the detected key equals the annotated key (same tonic and mode)
- **THEN** the song counts toward mode, exact, relative-aware, and collection accuracy

#### Scenario: A relative-only difference is a near-match
- **WHEN** the annotation is C major and the detection is A minor (its relative)
- **THEN** the song counts toward relative-aware accuracy
- **AND** it does NOT count toward exact accuracy

#### Scenario: A diatonic-degree detection counts toward collection accuracy
- **WHEN** the annotation is C major and the detection centers on a diatonic degree of C major other than the relative (e.g. E minor = the mediant iii, or G = the dominant V)
- **THEN** the song counts toward collection accuracy
- **AND** it does NOT count toward exact accuracy
- **AND** it does NOT count toward relative-aware accuracy (unless it is also the relative)

#### Scenario: A non-diatonic detection fails collection accuracy
- **WHEN** the detected tonic is not a diatonic degree of the annotated key (e.g. annotation A major, detection C major — C is not in the A-major scale)
- **THEN** the song does NOT count toward collection accuracy

#### Scenario: Metrics are nested by permissiveness
- **WHEN** a corpus is evaluated
- **THEN** relative-aware accuracy is greater than or equal to exact accuracy
- **AND** collection accuracy is greater than or equal to relative-aware accuracy

#### Scenario: Only annotated songs are evaluated
- **WHEN** the corpus is loaded from a directory
- **THEN** songs without an annotated key are excluded from the evaluation

#### Scenario: The baseline reports the collection metric per song and in aggregate
- **WHEN** `scripts/key_baseline.py` runs
- **THEN** the aggregate output includes a collection (key-signature) accuracy line alongside mode, exact, and relative-aware
- **AND** a song that matches the collection but not the exact center is shown with a distinct verdict (e.g. "coleção"), reserving the error verdict for a wrong diatonic collection
