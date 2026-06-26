## 1. Probabilistic functional parsing (`harmonic_analysis/domain/functional_hmm.py`)

- [x] 1.1 Define HMM states (function set) + functional-grammar transition priors
- [x] 1.2 Emission likelihoods bridging from the deterministic analyzer (chosen function high, plausible alternatives lower)
- [x] 1.3 Viterbi decode → most-probable functional path
- [x] 1.4 Per-chord confidence + alternative functions with probabilities
- [x] 1.5 Integrate: add `functional_parse` to the result
- [x] 1.6 Tests: C F G7 C → [T,SD,D,T]; D resolves to T as a likely transition; ambiguous chord lists alternatives; unambiguous chord high confidence

## 2. Reharmonization engine (`harmonic_analysis/domain/reharmonization.py`)

- [x] 2.1 Tritone substitution of a resolving dominant (G7→Db7) with rationale
- [x] 2.2 Secondary-dominant insertion before a diatonic target (… → A7 Dm)
- [x] 2.3 ii–V interpolation before a target
- [x] 2.4 Modal interchange + diatonic substitution suggestions
- [x] 2.5 Function-preserving guarantee + technique label + rationale + ranking/dedupe
- [x] 2.6 Integrate: `reharmonizations` section + `reharmonize` CLI subcommand
- [x] 2.7 Tests: G7→C suggests Db7 (tritone, dominant preserved); Dm gets A7 inserted; suggestions carry technique+rationale

## 3. Style fingerprint (`harmonic_analysis/domain/style_fingerprint.py`)

- [x] 3.1 Aggregate features over analyses: function distribution (normalized), transition matrix, cadence counts, modal usage, tension density
- [x] 3.2 Fingerprint comparison (similarity/distance)
- [x] 3.3 Integrate: `fingerprint` CLI subcommand over `--all`
- [x] 3.4 Tests: distribution sums to 1; self-similarity maximal; different corpora differ; fingerprint has all sections

## 4. Explanation layer (`Explainer` + pluggable `LLMProvider`)

- [x] 4.1 Define the `Explainer` port + `TemplateExplainer` (default, deterministic, offline): key, functions, cadences, SubV/Dsec, mode
- [x] 4.2 Define the `LLMProvider` port + provider registry (`PROVIDERS`) + per-provider default model (`DEFAULT_MODEL`) + `LLMConfig`/`build_llm_provider`
- [x] 4.3 `OpenRouterProvider` (default, OpenAI-compatible, `openrouter/free`, `OPENROUTER_API_KEY`) + `OllamaProvider` (local/offline) + `AnthropicProvider` (verify SDK/model via the claude-api reference)
- [x] 4.4 `LLMExplainer(provider)` (explains from the analysis) + `build_explainer`; graceful fallback to template on missing extra/key/network/unknown provider
- [x] 4.5 Integrate: `explanation` section + `explain` CLI subcommand (`--engine template|llm`, `--llm-provider`, `--llm-model`); gate LLM deps behind `[explain-llm]` extra
- [x] 4.6 Tests: template deterministic + offline; explains SubV referencing the tonic; states key + authentic cadence; no-config → template; LLM default = OpenRouter free; provider/model switchable; missing provider/key → graceful fallback

## 5. Validation & verification

- [x] 5.1 Per-capability test suites green
- [x] 5.2 Determinism check: the full offline path (HMM, reharmonization, fingerprint, template explainer) is reproducible
- [x] 5.3 Full suite green across all packages; ruff clean
- [x] 5.4 Real-cifra spot check (in-process): functional_parse, reharmonizations, explanation populated; no regression in existing sections
