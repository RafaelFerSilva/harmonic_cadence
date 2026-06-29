## ADDED Requirements

### Requirement: Reports name the modal center when coloring is present

The Markdown, HTML, and explanation reports SHALL render the tonal center named by its Greek mode when a `modal_coloring` annotation is present, fusing the tonic of `detect_key` (spelled via `Note`) with the flavor (e.g. "D mixolídio", "D frígio") alongside the tonal reading and its coloring evidence.

The naming MUST be a pure presentation promotion of an already-computed field: it MUST NOT alter `detect_key`, `detect_coloring`, the canonical analysis JSON, or any baseline metric.

When no `modal_coloring` is present, the center heading SHALL remain the plain tonal reading
(e.g. "D maior"), byte-identical to prior behaviour. Only `mixolydian` and `phrygian` are
nameable (the flavors `detect_coloring` emits); aeolian stays silent (natural minor needs no
modal label) and dorian is never named here (it shares a collection with mixolydian and
belongs to curated annotation, not algorithmic detection).

#### Scenario: Mixolydian center is named when coloring fires

- **WHEN** an analysis whose detected key is D major and whose `modal_coloring` flavor is `mixolydian` is rendered
- **THEN** the report names the center "D mixolídio"
- **AND** the coloring evidence (e.g. bVII→I and its positions) is still shown as detail
- **AND** the canonical analysis JSON (`key`, `mode`, `modal_coloring`) is unchanged

#### Scenario: Phrygian center is named when coloring fires

- **WHEN** an analysis whose detected key is D minor and whose `modal_coloring` flavor is `phrygian` is rendered
- **THEN** the report names the center "D frígio"
- **AND** the key/mode heading still reflects the tonal reading (the naming does not replace `detect_key`)

#### Scenario: No coloring leaves the tonal heading unchanged

- **WHEN** an analysis with no `modal_coloring` (e.g. a plain major or an aeolian minor piece) is rendered
- **THEN** the center heading is the plain tonal reading (e.g. "D maior") identical to prior behaviour
- **AND** no Greek mode name is introduced (aeolian is not labeled; dorian is never named)

#### Scenario: Baseline parity is preserved

- **WHEN** the key-detection baseline is re-run after the change
- **THEN** the four Cifra-Club metrics, the structural-center accuracy, and the modulating numbers are identical to before
- **AND** the modal-coloring detection results are unchanged (the change only promotes the display of an existing field)
