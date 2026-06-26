## Context

O resultado de `AnalysisService.analyze_song_data_structured` já carrega, além das seções clássicas, as seções de Camada 2 (`tonal_regions`, `modal_analysis`, `roman_numerals`, `voice_leading`, `chord_scales`) e Camada 3 (`functional_parse`, `reharmonizations`, `explanation`). Os três geradores em `presentation/reports` (`JSONReportGenerator`, `MarkdownReportGenerator`, `HTMLReportGenerator`) montam uma saída curada e antiga e **ignoram** essas chaves. Esta mudança é puramente de apresentação.

## Goals / Non-Goals

**Goals:**
- Exibir as seções de profundidade e inteligência nos três formatos.
- Omitir graciosamente seções ausentes/vazias (sem quebrar nem poluir).
- Preservar exatamente as seções já existentes.

**Non-Goals:** mudar a análise ou o formato do dict de resultado; novos formatos; i18n; redesign visual do HTML.

## Decisions

### D1 — Renderização explícita por seção (não dump genérico)
Cada formato continua montando a saída com seções nomeadas e formatadas à mão (estilo atual), agora incluindo as novas. Não se faz `json.dump(result)` cru nem reflexão genérica.
- **Por quê:** mantém os relatórios legíveis e estáveis; cada seção tem a melhor representação no seu formato (tabela vs. lista vs. cartão); evita vazar chaves internas (`cifra_html`, flags de sucesso).
- **Alternativa:** despejar o dict inteiro — rejeitado (ilegível, frágil, expõe ruído).

### D2 — Helper de omissão graciosa
Um auxiliar por gerador decide se a seção entra: `None`, lista/dict vazio ou ausente ⇒ a seção é pulada. No JSON, a chave é omitida (não emitida como `null`); no Markdown/HTML, o bloco não é escrito.
- **Por quê:** `modal_analysis` é `None` em peças tonais; `reharmonizations` pode ser `[]`; a explicação pode faltar. A saída precisa permanecer válida e limpa.

### D3 — Representação por formato
- **JSON:** passthrough estruturado das seções (as estruturas já são serializáveis: `functional_parse`/`reharmonizations` vêm de `to_dict()`); agrupadas sob chaves claras (`depth`, `intelligence`) ou no topo — manter plano e nomeado.
- **Markdown:** tabela de cifragem romana; lista de regiões tonais; condução de vozes (linha de baixo) e escala-acorde em listas; reharmonizações como lista "original → resultado + justificativa"; explicação como parágrafo; parsing funcional como tabela acorde/função/confiança.
- **HTML:** um bloco/seção por item, reusando o estilo existente do template.

### D4 — Sem mudança de contrato dos geradores
A assinatura `generate(analysis, filename=None) -> str` e a `ReportFactory` ficam iguais. Só o corpo dos `generate` (e helpers privados) muda.

## Risks / Trade-offs

- **HTML é o maior arquivo (390 linhas, template inline)** → adicionar seções com cuidado para não quebrar o layout; teste verifica presença de marcadores das novas seções.
- **Reharmonizações podem ser muitas** (peças longas geram dezenas) → exibir as N mais idiomáticas por formato, com nota de truncamento, em vez de despejar todas.
- **Determinismo** → a `explanation` exibida é o template offline (padrão); nenhum relatório depende de LLM.

## Migration Plan

1. JSON: incluir as seções novas (omitindo as ausentes); manter as chaves atuais.
2. Markdown: novos blocos (RNA, regiões tonais, condução de vozes, escala-acorde, parsing funcional, reharmonizações, explicação).
3. HTML: seções equivalentes no template.
4. Testes de apresentação por formato (presença + omissão graciosa + sem regressão).
