## ADDED Requirements

### Requirement: Explainer port with a deterministic default

The system SHALL expose an `Explainer` port that turns a harmonic analysis into a human-readable explanation, with a default `TemplateExplainer` that is deterministic and works offline. The analysis MUST NOT require any explainer beyond the default.

#### Scenario: Default explainer is deterministic and offline
- **WHEN** the `TemplateExplainer` explains the same analysis twice
- **THEN** it returns the same text both times
- **AND** it makes no network request

#### Scenario: Explanation references the analysis
- **WHEN** an analysis containing a `SubV` (tritone substitute) is explained
- **THEN** the explanation names the substitute and the tonic it resolves to

#### Scenario: Explanation covers key and cadence
- **WHEN** an analysis with a detected key and an authentic cadence is explained
- **THEN** the explanation states the key and mentions the authentic cadence

### Requirement: Optional LLM explainer over a pluggable provider layer

The system SHALL allow an optional `LLMExplainer` backed by a pluggable `LLMProvider` (e.g. OpenRouter, Ollama, Anthropic), selected only by explicit configuration. The provider and the model MUST be switchable by configuration without changing the explainer, and new providers MUST be addable as adapters in a registry. When the LLM engine is enabled without further choice, the default provider/model SHALL be a free option.

#### Scenario: No engine configured uses the deterministic default
- **WHEN** no LLM engine is configured
- **THEN** the active explainer is the `TemplateExplainer`

#### Scenario: LLM default provider and model are free
- **WHEN** the LLM engine is enabled without specifying a provider or model
- **THEN** the provider is OpenRouter and the model is its free router (`openrouter/free`)

#### Scenario: Provider and model are switchable by configuration
- **WHEN** the configuration selects a different provider and/or model (e.g. a local Ollama model)
- **THEN** the explainer uses that provider/model without any code change

#### Scenario: Missing provider dependency or credentials degrades gracefully
- **WHEN** the LLM engine is requested but the provider extra, credentials, or network are unavailable (or the provider name is unknown)
- **THEN** the system falls back to the deterministic `TemplateExplainer`
- **AND** the analysis still produces an explanation
