## ADDED Requirements

### Requirement: Corpus tipado de vereditos de trítono com citação obrigatória

O sistema SHALL manter um corpus curado, tipado e em código
(`harmonic_analysis.corpus.tritone_adjudications`) de **vereditos** para as ocorrências do
ledger de trítono não-dominante. Cada veredito SHALL ser identificado pela música + posição
(a mesma identidade do `v_ledger_tritone_nondominant`) e SHALL carregar uma **citação Chediak
obrigatória** (obra, volume, página). A ausência ou malformação da citação SHALL falhar rápido
na importação do módulo — sem página, o fato não existe (muro de copyright = só fatos citados;
nunca texto/tabela/cifra do livro). O corpus é camada de **anotação (PRATA)**: SHALL NOT
reescrever `function_code`, `degree` ou qualquer saída do coder.

#### Scenario: Veredito sem citação é rejeitado na importação

- **WHEN** um `TritoneVerdict` é construído sem citação, ou com página/volume inválidos
- **THEN** a construção SHALL levantar erro (falha-rápido na importação), de modo que o corpus
  nunca contenha um veredito sem página citável

#### Scenario: Corpus não muta a saída do coder

- **WHEN** o corpus de adjudicação é importado e consultado durante um `corpus build`/`report`
- **THEN** os valores `function_code` e `degree` de toda ocorrência SHALL permanecer idênticos
  aos que o motor produziu — a adjudicação anota, nunca sobrescreve

### Requirement: Enum fechado de veredito, resíduo ambíguo declarado

O sistema SHALL restringir o veredito a um conjunto fechado de categorias geométricas
(`subv`, `chromatic_approach`, `emp_legitimate`, `dsec_deceptive`, `ambiguous`). O caso
genuinamente indecidível SHALL ser marcado `ambiguous` com nota do porquê — nunca forçado a
uma categoria — para que o resíduo honesto seja **declarado**, não escondido.

#### Scenario: Veredito fora do enum é rejeitado

- **WHEN** um veredito é criado com uma categoria fora do conjunto fechado
- **THEN** a construção SHALL falhar, garantindo que todo veredito é uma das categorias
  geométricas citáveis (ou `ambiguous` explícito)

#### Scenario: Lookup por ocorrência

- **WHEN** o veredito de uma ocorrência do ledger (música + posição) é buscado
- **THEN** o sistema SHALL retornar o `TritoneVerdict` curado, ou `None` se aquela ocorrência
  ainda não foi adjudicada (miss explícito, nunca um veredito inventado)

### Requirement: Auditoria anti-drift do ledger adjudicado

O sistema SHALL fornecer uma auditoria (`scripts/audit_tritone_adjudication.py`, molde de
`audit_completeness.py`) que re-deriva as ocorrências do ledger de trítono com a extração
corrente e verifica que **toda** ocorrência está adjudicada OU marcada `ambiguous`
explicitamente. A auditoria SHALL falhar (código de saída não-zero) quando houver ocorrência do
ledger sem veredito, ou veredito órfão (para ocorrência que não está mais no ledger) — de modo
que crescer o corpus ou mudar a extração nunca deixe resíduo silencioso.

#### Scenario: Ocorrência não-adjudicada acusa drift

- **WHEN** o ledger corrente contém uma ocorrência sem entrada no corpus de adjudicação
- **THEN** a auditoria SHALL reportar a ocorrência faltante e sair com código não-zero

#### Scenario: Corpus alinhado ao ledger passa

- **WHEN** toda ocorrência do ledger tem veredito e todo veredito aponta para uma ocorrência
  ainda presente no ledger
- **THEN** a auditoria SHALL sair com código zero e reportar a contagem por veredito

### Requirement: Vereditos cruzados no relatório de corpus

O relatório `harmonic corpus report` SHALL exibir a distribuição das ocorrências do ledger de
trítono por veredito (com denominador visível), **nunca como placar de acerto/erro** — é uma
foto descritiva da curadoria, não uma métrica de acurácia do coder.

#### Scenario: Report mostra a contagem por veredito

- **WHEN** `corpus report` roda sobre um corpus com ocorrências de trítono adjudicadas
- **THEN** a saída SHALL incluir a contagem por categoria de veredito (incl. `ambiguous`) com
  o total de ocorrências visível, sem linguagem de acerto/erro
