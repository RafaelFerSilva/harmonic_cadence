## Why

As Camadas 1–2 deram **correção** (altura/spelling, tonalidade, dominantes) e **profundidade** (modos, cifragem romana, condução de vozes, escala-acorde). O que falta para ser de fato estado da arte é **inteligência**: passar de *descrever* a harmonia para *raciocinar* sobre ela.

- A análise funcional é **determinística e de resposta única**. Harmonia é ambígua: um acorde pode ter mais de uma função; hoje não há hipóteses alternativas nem confiança.
- A ferramenta **só analisa**, não **cria**. Um músico quer sugestões de reharmonização (trítono-sub, dominante secundário, interpolação de ii-V, intercâmbio modal).
- Há cache de muitas músicas e `--all`, mas **nenhuma análise de corpus**: não dá para extrair o "DNA harmônico" de um artista/gênero nem comparar estilos.
- A saída é estruturada, **não explicada**: falta uma camada que ensine ("por que esse Db7 é um SubV de C").

Esta mudança entrega a **camada de inteligência** (Camada 3) sobre toda a fundação anterior.

## What Changes

- Introduzir **parsing funcional probabilístico** (`probabilistic-functional-parsing`): modelar função como cadeia de Markov oculta e usar Viterbi para o caminho funcional mais provável, com **confiança por acorde** e **parses alternativos** para acordes ambíguos — complementando (não removendo) a análise determinística atual.
- Introduzir um **motor de reharmonização** (`reharmonization`): sugestões idiomáticas (substituto de trítono, inserção de dominante secundário, interpolação de ii-V, intercâmbio modal, substituição diatônica) com rótulo de técnica e justificativa, preservando a função.
- Introduzir **impressão digital de estilo** (`style-fingerprint`): agregar features harmônicas (distribuição de funções, matriz de transição, cadências, tensões, uso modal) sobre um conjunto de músicas e comparar fingerprints.
- Introduzir uma **camada de explicação** (`harmonic-explanation`): porta `Explainer` com adaptador **determinístico por template (padrão, offline)** e adaptador **Claude opcional**, gerando explicação pedagógica em prosa a partir da análise.
- Expor novas seções/saídas no resultado e novos subcomandos de CLU (`reharmonize`, `fingerprint`, `explain`).

Fora de escopo: re-treinar/alterar a fundação das Camadas 1–2; transcrição de áudio; geração de partitura/MIDI. Esta change é a camada de raciocínio sobre a análise existente.

## Capabilities

### New Capabilities
- `probabilistic-functional-parsing`: caminho funcional mais provável via HMM/Viterbi, com confiança e parses alternativos para ambiguidade.
- `reharmonization`: sugestões de reharmonização idiomáticas (trítono-sub, dominante secundário, ii-V, intercâmbio modal, substituição diatônica) com técnica e justificativa.
- `style-fingerprint`: agregação de features harmônicas por conjunto/artista e comparação de fingerprints.
- `harmonic-explanation`: explicação pedagógica via porta `Explainer` (template determinístico padrão + adaptador Claude opcional).

### Modified Capabilities
<!-- Nenhuma: todas as capacidades são novas e aditivas; a análise determinística das Camadas 1–2 permanece intacta. -->

## Impact

- **Código (`harmonic_analysis/domain`)**: novos módulos `functional_hmm.py`, `reharmonization.py`, `style_fingerprint.py`; reusam funções/graus/cadências/escala-acorde já existentes.
- **Código (explicação)**: porta `Explainer` (`TemplateExplainer` padrão determinístico + `LLMExplainer`) **e** uma camada de provedores `LLMProvider` plugável (`OpenRouterProvider`, `OllamaProvider`, `AnthropicProvider`) com registro e config — provedor e modelo escolhíveis de forma simples.
- **Dependência externa opcional + gratuita por padrão**: quando o LLM é acionado, o padrão é **OpenRouter** com `openrouter/free` (modelo gratuito), via `OPENROUTER_API_KEY`. **Estritamente opt-in**, atrás do extra `[explain-llm]`. O padrão geral (template) é offline/determinístico; a ausência de extra/chave/provedor **degrada para o template**, nunca quebra a análise.
- **Resultado/relatórios**: novas seções (`functional_parse`, `reharmonizations`, `explanation`) e, para corpus, um relatório de fingerprint via `--all`.
- **CLI**: subcomandos `reharmonize`, `fingerprint`, `explain` (o `explain` aceita `--engine template|llm` e `--llm-provider`/`--llm-model`).
- **Determinismo preservado**: HMM/Viterbi, reharmonização, fingerprint e o template explainer são determinísticos e offline; só o `ClaudeExplainer` é não-determinístico e opcional.
- **Sem impacto** em scraping, providers de cifra, cache ou empacotamento do core.
