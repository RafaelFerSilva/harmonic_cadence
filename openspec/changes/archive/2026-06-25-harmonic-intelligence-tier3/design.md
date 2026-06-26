## Context

Camadas 1–2 entregaram correção e profundidade determinísticas: altura/spelling (`cifra_core/theory`), tonalidade (Krumhansl-Schmuckler + modulação), dominantes aplicados, modos de 1ª classe, cifragem romana com inversões, condução de vozes e escala-acorde/tensões. `AnalysisService` já produz funções, cadências, progressões, regiões tonais e as seções da Camada 2. Esta camada adiciona **raciocínio** sobre essa base: parsing probabilístico, reharmonização, impressão digital de estilo e explicação.

## Goals / Non-Goals

**Goals:**
- Caminho funcional mais provável (HMM/Viterbi) com confiança e alternativas.
- Sugestões de reharmonização idiomáticas, rotuladas e justificadas.
- Impressão digital de estilo por corpus e comparação.
- Explicação pedagógica via porta, com padrão determinístico offline e Claude opcional.

**Non-Goals:** alterar a fundação das Camadas 1–2; transcrição de áudio; geração de partitura/MIDI; treinar modelos de ML.

## Decisions

### D1 — Parsing funcional por HMM + Viterbi (determinístico)
Estados = funções harmônicas (T, SD, D, Dsec, SubV, Modal, …). Emissão = verossimilhança acorde→função, derivada do **analisador determinístico existente** (a função que ele já atribui recebe alta probabilidade; alternativas plausíveis recebem massa menor por priors de qualidade/grau). Transição = gramática funcional (D→T forte, T→SD/D, SD→D, etc.). Decodificação por Viterbi.
- **Por quê:** padrão, interpretável, determinístico; modela a ambiguidade que a resposta única de hoje ignora; reusa a Camada 2 como ponte de emissão.
- **Alternativa:** treinar um modelo num corpus anotado — rejeitado (sem corpus; priors teóricos bastam e são explicáveis).

### D2 — Reharmonização como biblioteca de transformações regradas
Cada técnica (trítono-sub, inserção de dominante secundário, interpolação de ii-V, intercâmbio modal, substituição diatônica) é uma função `progressão → sugestões`, reusando `applied-dominant-analysis`, `chord-scale-tensions` e `modal-tonal-center`. Cada sugestão preserva a função e carrega técnica + justificativa. Ranqueia por fit idiomático e deduplica.
- **Por quê:** determinístico, explicável e fiel à teoria; é o que um arranjador reconhece.
- **Alternativa:** geração por LLM — rejeitado para o núcleo (não-determinístico); o LLM entra só na explicação (D4).

### D3 — Fingerprint como vetor de features agregado
Sobre N análises (via `--all`), agregar: distribuição de funções (normalizada), matriz de transição função→função, contagem de cadências, uso modal e densidade de tensões. Comparar fingerprints por similaridade (cosseno / Jensen-Shannon na distribuição + transição).
- **Por quê:** captura o "DNA harmônico" de artista/gênero de forma simples e comparável; reusa o batch existente.

### D4 — Explicação por porta `Explainer` + camada de provedores de LLM plugável
Duas portas em composição: `Explainer` (análise→prosa) e `LLMProvider` (chat/completion, abstrai o **provedor de IA e o modelo**). `TemplateExplainer` (padrão geral): determinístico e offline, **sem LLM**. `LLMExplainer(provider)`: usa um `LLMProvider` injetado para explicar a partir da análise. Adaptadores de provedor num registro extensível: `OpenRouterProvider` (padrão de LLM), `OllamaProvider` (local/offline), `AnthropicProvider` — escolha de provedor + modelo por configuração.
- **Gratuito por padrão:** quando o LLM é acionado, o provedor padrão é **OpenRouter** com o modelo **`openrouter/free`** (roteia automaticamente para um modelo gratuito e informa qual usou). Trocar de modelo = mudar a string; trocar de provedor = trocar o adaptador no registro. Tudo opt-in, atrás do extra `[explain-llm]`.
- **Por quê:** flexibilidade de provedor/modelo sem reescrever o explainer; custo zero por padrão; OpenRouter é **OpenAI-compatível** (a mesma SDK serve para OpenRouter, Ollama e outros — só mudam `base_url`/chave). O `TemplateExplainer` permanece o padrão geral: offline, sem chave, determinístico.
- **Alternativa:** amarrar num provedor único (ex.: só Claude) — rejeitado pela falta de flexibilidade e por não ser gratuito por padrão.

### D5 — Aditivo; novos subcomandos e seções
Novos módulos em `harmonic_analysis/domain`; novas seções no resultado (`functional_parse`, `reharmonizations`, `explanation`); novos subcomandos `reharmonize`, `fingerprint`, `explain`. Seções e comandos existentes inalterados. Tudo determinístico e offline, exceto o `ClaudeExplainer` opt-in.

## Risks / Trade-offs

- **Probabilidades do HMM são ajustadas à mão (sem treino)** → codificar priors teóricos; validar o caminho em progressões conhecidas; expor confiança em vez de afirmar certeza.
- **Reharmonização combinatória** → limite de sugestões por ponto, ranqueamento e dedupe.
- **LLM: custo, não-determinismo, chave, rede** → estritamente opt-in, template como padrão, fallback gracioso, nunca obrigatório; limitar/cachear chamadas.
- **Fingerprint pouco significativo com poucas músicas** → funciona com qualquer N; documentar a ressalva de N pequeno.
- **Escopo (4 capacidades)** → módulos independentes; entregar e validar uma a uma.

## Migration Plan

1. `functional_hmm.py`: estados, emissão (do analisador determinístico), transições, Viterbi; seção `functional_parse` + confiança/alternativas.
2. `reharmonization.py`: transformações por técnica + ranqueamento; subcomando `reharmonize` + seção.
3. `style_fingerprint.py`: agregação de features + comparação; subcomando `fingerprint` sobre `--all`.
4. Porta `Explainer` + `TemplateExplainer` (padrão) + `ClaudeExplainer` opcional (extra `[explain-llm]`); subcomando `explain` (`--engine template|claude`) + seção `explanation`.
5. Testes por capacidade + extensão de corpus; provar determinismo do caminho offline.

## Resolved Decisions

As quatro questões abertas ficam decididas:

- **Transições do HMM:** gramática **fixada à mão** com priors teóricos (Appendix A); o catálogo `PROGRESSIONS` existente serve de **validação** (o caminho decodificado deve concordar com progressões conhecidas), não de fonte de probabilidades.
- **Ranqueamento da reharmonização:** por **frequência idiomática** — técnicas comuns (trítono-sub, ii-V) antes das raras —, com dedupe; a distância harmônica é desempate secundário.
- **Provedor/modelo de LLM padrão:** **OpenRouter + `openrouter/free`** (gratuito), atrás de uma camada de provedores plugável; trocável por config (provedor e modelo) — Ollama (local) e Anthropic como adaptadores adicionais (ver D4 / Appendix B).
- **Distância do fingerprint:** **cosseno** sobre o vetor de features concatenado (distribuição + transição achatada); Jensen-Shannon fica como métrica alternativa exposta para as distribuições.

## Appendix A — HMM funcional (detalhe)

Contrato concreto da decisão **D1**.

### Estados
Conjunto enxuto de macro-funções para a gramática, com os especiais mapeados:
`T` (tônica), `SD` (subdominante), `D` (dominante), `X` (transitório: Emp/Modal/Dim/Crom/Outro).
Os aplicados **Dsec/SubV** participam da transição como `D` (resolvem como dominante), mas são **rotulados à parte** na saída (o rótulo vem do analisador determinístico; o HMM só decide a macro-função).

### Transição (priors da gramática funcional — linhas = de, colunas = para)
```
        T     SD    D     X
T      .30   .35   .25   .10
SD     .10   .15   .60   .15      D→T forte; SD→D forte; T→SD/D; X transitório
D      .65   .05   .15   .15
X      .35   .25   .25   .15
```
Valores ilustrativos e ajustáveis; somam 1 por linha. Início: prior favorecendo `T`.

### Emissão (ponte da Camada 2)
`P(acorde | estado)` deriva do analisador determinístico: a macro-função `f0` que ele já atribui recebe a maior massa (ex.: `0.7`); o restante (`0.3`) é distribuído sobre alternativas plausíveis por priors de qualidade/grau (ex.: um `vi` menor → `{T:.6, SD:.2, X:.2}`). Mantém a Camada 3 consistente com a 2.

### Decodificação e confiança
- **Caminho:** Viterbi padrão maximizando `∏ emissão·transição` → macro-função mais provável por acorde.
- **Confiança/alternativas:** marginais posteriores por posição via **forward-backward**; `confiança = posterior(escolhida)`, `alternativas = demais estados ordenados por posterior`. Determinístico (sem amostragem).

## Appendix B — `Explainer` + camada de provedores de LLM (detalhe)

Contrato concreto da decisão **D4**: duas portas em composição (explicação e provedor de IA), espelhando o padrão `SongProvider`.

### Porta de explicação
```python
@runtime_checkable
class Explainer(Protocol):
    def explain(self, analysis: dict) -> str: ...

class TemplateExplainer:        # PADRÃO — determinístico, offline, SEM LLM
    def explain(self, analysis): ...   # prosa a partir de key/funções/cadências/SubV/Dsec/modo

class LLMExplainer:             # usa um provedor de LLM injetado
    def __init__(self, provider: "LLMProvider"):
        self.provider = provider
    def explain(self, analysis):
        system, user = build_prompt(analysis)   # explica a PARTIR da análise (não re-analisa)
        return self.provider.complete(system, user)
```

### Porta de provedor de IA (provedor + modelo plugáveis)
```python
@runtime_checkable
class LLMProvider(Protocol):
    def complete(self, system: str, user: str) -> str: ...

# Provedores OpenAI-compatíveis (OpenRouter, Ollama) compartilham um cliente HTTP;
# só mudam base_url e chave. Anthropic usa sua própria SDK.
class OpenRouterProvider:   # PADRÃO de LLM — base_url=https://openrouter.ai/api/v1
    def __init__(self, model="openrouter/free", api_key=None): ...   # OPENROUTER_API_KEY
class OllamaProvider:       # local/offline, sem chave — base_url=http://localhost:11434/v1
    def __init__(self, model="llama3.1", api_key=None): ...
class AnthropicProvider:    # SDK Anthropic
    def __init__(self, model="claude-haiku-4-5-20251001", api_key=None): ...

PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "anthropic": AnthropicProvider,
}
# modelo-padrão por provedor (gratuito quando possível)
DEFAULT_MODEL = {
    "openrouter": "openrouter/free",
    "ollama": "llama3.1",
    "anthropic": "claude-haiku-4-5-20251001",
}
```

### Configuração e raiz de composição
```python
@dataclass
class LLMConfig:
    provider: str = "openrouter"          # registro PROVIDERS
    model: Optional[str] = None           # None → DEFAULT_MODEL[provider]
    api_key: Optional[str] = None         # senão, env por provedor
    base_url: Optional[str] = None

def build_llm_provider(cfg: LLMConfig) -> LLMProvider:
    cls = PROVIDERS[cfg.provider]         # KeyError → fallback no explainer
    return cls(model=cfg.model or DEFAULT_MODEL[cfg.provider], api_key=cfg.api_key)

def build_explainer(cfg) -> Explainer:
    if cfg.engine == "llm":
        try:
            return LLMExplainer(build_llm_provider(cfg.llm))
        except (ImportError, KeyError, MissingCredentials):
            return TemplateExplainer()    # fallback gracioso
    return TemplateExplainer()
```

Regras de contrato:
- **Padrão geral** = `TemplateExplainer`: determinístico, offline, sem chave; a análise jamais depende de LLM.
- **Padrão de LLM** (quando `engine="llm"`) = `OpenRouterProvider` + `openrouter/free` → **gratuito**.
- **Trocar modelo:** mudar a string (`cfg.llm.model`). **Trocar provedor:** mudar `cfg.llm.provider` (registro). **Adicionar provedor:** registrar um adaptador novo em `PROVIDERS` — sem tocar no `LLMExplainer`.
- O LLM **explica a partir da análise determinística** (fundamentado, auditável; não re-analisa).
- Qualquer falha (extra/dep ausente, sem chave, sem rede, provedor desconhecido) **degrada para o template** — nunca quebra a análise.
- Seleção só por configuração explícita (`--engine llm [--llm-provider X] [--llm-model Y]`); sem config → template.
