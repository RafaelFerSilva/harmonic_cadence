## Why

As Camadas 2 e 3 enriqueceram o resultado da análise com profundidade (modos, cifragem romana, condução de vozes, escala-acorde) e inteligência (parsing funcional probabilístico, reharmonização, explicação). Mas os **relatórios humanos** (`html`, `markdown`, `json`) renderizam um subconjunto fixo e **antigo** — descartam todas essas seções, mesmo elas já existindo no dicionário de resultado. O usuário que gera um relatório não vê o que a ferramenta passou a saber.

## What Changes

- Renderizar nos três formatos de relatório as seções de **profundidade** já presentes no resultado: `tonal_regions`, `modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`.
- Renderizar as seções de **inteligência**: `functional_parse` (com confiança/alternativas), `reharmonizations` (técnica + justificativa) e `explanation` (prosa pedagógica).
- Cada formato apresenta as seções no seu idioma: **JSON** as expõe estruturadas; **Markdown** em tabelas/listas + prosa; **HTML** em blocos/cartões legíveis.
- **Omissão graciosa**: seção ausente, `None` ou vazia (ex.: `modal_analysis` numa peça tonal, `reharmonizations` vazia) é simplesmente omitida — o relatório continua válido.
- **Compatibilidade**: as seções atuais (estatísticas, tabela de acordes, cadências, cifra) continuam idênticas; nada é removido nem renomeado.

Fora de escopo: alterar a análise ou qualquer seção do resultado; novos formatos de relatório; internacionalização; estilização visual além do necessário para exibir as seções.

## Capabilities

### New Capabilities
- `analysis-reporting`: contrato dos relatórios gerados — quais seções da análise (profundidade e inteligência) cada formato deve exibir, e a regra de omissão graciosa para seções ausentes.

### Modified Capabilities
<!-- Nenhuma: as capacidades de análise (Camadas 1–3) permanecem intactas; esta mudança é puramente de apresentação. -->

## Impact

- **Código (`harmonic_analysis/presentation/reports`)**: `json.py`, `markdown.py`, `html.py` passam a ler e renderizar as seções novas a partir do dict de resultado; `base.py`/`factory.py` inalterados (mesma interface `generate(analysis) -> path`).
- **Sem impacto** no domínio, serviços, scraping, providers ou CLI — os dados já existem no resultado; só a camada de apresentação muda.
- **Saída**: os arquivos `report_json/`, `report_markdown/` e `report_html/` passam a conter as seções de Camada 2 e 3. Determinístico (a `explanation` padrão é o template offline).
- **Testes**: novos testes de apresentação garantindo presença das seções e a omissão graciosa, sem regressão das seções existentes.
