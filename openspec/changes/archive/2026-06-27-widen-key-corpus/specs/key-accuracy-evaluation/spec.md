## ADDED Requirements

### Requirement: Real-song baseline uses the source's own key as independent gold

The real-song key-detection baseline SHALL annotate each song with the **source's
own key** (the Cifra Club "tom") as the gold, rather than an external authority.
Because the gold and the chords come from the same source, there is **no
transposition gap**, so exact-tonic accuracy is a meaningful first-class metric for
this baseline (not merely a relative-aware approximation).

The baseline corpus SHALL be a committed list of **facts** — `(artist, song, key)`
— and MUST NOT store the chord sheets themselves; the chords are fetched at run time
and discarded. This keeps the corpus independent and within the project's source
boundary (the book's analyzed-song tables are not ingested as fixtures).

#### Scenario: Gold annotation is the source key, not an external authority

- **WHEN** a song is evaluated in the real-song baseline
- **THEN** its gold key is the key annotated by the chord source (Cifra Club)
- **AND** the detected key is compared against that same-source gold

#### Scenario: Exact-tonic accuracy is meaningful (no transposition confound)

- **WHEN** the baseline reports its metrics
- **THEN** exact-tonic accuracy reflects detection quality directly, because gold and
  chords share one source and are not transposed relative to each other

#### Scenario: Only facts are stored, not chord sheets

- **WHEN** the baseline corpus is committed to the repository
- **THEN** it contains only `(artist, song, key)` facts
- **AND** no chord sheet content is stored; chords are re-fetched at run time

#### Scenario: Corpus is curated against real fetchability

- **WHEN** a candidate song cannot be fetched or carries no source key
- **THEN** it is excluded from the committed corpus
- **AND** the corpus reflects only songs verified to fetch with an annotated key
