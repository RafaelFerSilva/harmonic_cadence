# tonal-center-adjudication Specification

## Purpose

Manter uma camada de **anotação (PRATA)** sobre a worklist de centro tonal: um corpus curado,
tipado e em código de **vereditos** citados de Chediak para cada música em que os dois métodos do
motor — `detect_key` (K-S) e `chediak_functional_center` (achador funcional) — DIVERGEM
(`center_status = 'diverge'`). Cada veredito anota **quem acertou** (`detect`/`functional`/
`neither_ii_v`/`modulating`/`ambiguous`) com a evidência visível da própria música (a cadência que
decide) e uma **citação Chediak obrigatória** (o critério funcional, pp.84-85/87) — sem página o
fato não existe (muro de copyright = só fatos citados; o resíduo genuinamente indecidível é
DECLARADO `ambiguous`, não escondido). O corpus **anota, nunca reescreve**: `detect_key`,
`chediak_functional_center`, `center_pc`/`center_status` e qualquer saída do motor permanecem
intocados; uma auditoria anti-drift garante que crescer o corpus ou mudar a extração nunca deixe
divergência sem veredito nem veredito órfão.

Esta capability é **distinta de `modal-center-arbitration`**: aquela anota o centro **modal grego**
que a cifra do CC não codifica mas Chediak documenta (Arrastão → Lá dórico); esta adjudica a
**divergência de centro tonal entre dois métodos do próprio motor**, um problema interno de
detecção, não uma anotação de fato modal ausente do dado.

## Requirements

### Requirement: Corpus tipado de vereditos de centro com citação obrigatória

O sistema SHALL manter um corpus curado, tipado e em código
(`harmonic_analysis.corpus.tonal_center_adjudications`) de **vereditos** para as músicas onde
`detect_key` e `chediak_functional_center` DIVERGEM. Cada veredito SHALL ser identificado pelo
slug da música e SHALL carregar o **centro tonal adjudicado** (raiz + modo `major`/`minor`), a
**evidência** (a cadência visível que decide, da própria música) e uma **citação Chediak
obrigatória** (o critério funcional, pp.84-85/87). A ausência ou malformação da citação SHALL
falhar rápido na importação — sem página o fato não existe (exceto o veredito `ambiguous`, que
exige nota em vez de citação). O corpus é camada de **anotação (PRATA)**: SHALL NOT alterar
`detect_key`, `chediak_functional_center`, `center_pc`/`center_status` nem qualquer saída do motor.

#### Scenario: Veredito decisivo sem citação é rejeitado

- **WHEN** um `TonalCenterVerdict` não-`ambiguous` é construído sem citação
- **THEN** a construção SHALL levantar erro (falha-rápido na importação), de modo que todo
  veredito decisivo tenha página citável

#### Scenario: Corpus não altera a detecção do motor

- **WHEN** o corpus de adjudicação é importado e consultado durante `corpus build`/`report`
- **THEN** o `center_status`/`center_pc` de toda música SHALL permanecer idêntico ao que o motor
  produziu — a adjudicação anota, nunca sobrescreve a detecção

### Requirement: Enum fechado de veredito, modulante e ambíguo declarados

O sistema SHALL restringir o `winner` a um conjunto fechado que codifica o achado do #7 (não há
regra-cega): `detect` (o `detect_key` acertou; o achador funcional pegou um v/ii/pivô tonicizado),
`functional` (o critério funcional acertou; o K-S pegou V/IV/ii/iii/relativa), `neither_ii_v` (a
armadilha do ii-V: nenhum dos dois pegou a tônica, que é o alvo do V), `modulating` (sem centro
global único), `ambiguous` (indecidível pela cadência visível). Os casos `modulating`/`ambiguous`
SHALL trazer nota do porquê — o resíduo honesto é DECLARADO, nunca forçado a um vencedor.

#### Scenario: Winner fora do enum é rejeitado

- **WHEN** um veredito é criado com um `winner` fora do conjunto fechado
- **THEN** a construção SHALL falhar

#### Scenario: Lookup por música

- **WHEN** o veredito de uma música da worklist é buscado por slug
- **THEN** o sistema SHALL retornar o `TonalCenterVerdict` curado, ou `None` se a música ainda
  não foi adjudicada (miss explícito, nunca um veredito inventado)

### Requirement: Worklist de centro como view com veredito cruzado

O sistema SHALL expor uma view aditiva `v_center_worklist` que lista as músicas
`center_status = 'diverge'` com o `detect_key`, o centro funcional e — quando adjudicada — o
`winner`, o centro adjudicado e a página citada (LEFT JOIN à tabela derivada `center_adjudication`,
regenerável no build). Música ainda não adjudicada SHALL aparecer com veredito nulo (não some da
view). O `harmonic corpus report` SHALL mostrar a distribuição por `winner` com denominador
visível, **nunca** como acurácia/placar do detector.

#### Scenario: View lista divergências com e sem veredito

- **WHEN** a view `v_center_worklist` é consultada
- **THEN** ela SHALL retornar toda música `diverge` com detect/funcional, e o `winner`+página
  quando adjudicada (NULL caso contrário) — insumo de curadoria, nunca placar

#### Scenario: Report mostra a distribuição por veredito

- **WHEN** `corpus report` roda sobre um corpus com divergências adjudicadas
- **THEN** a saída SHALL incluir a contagem por `winner` (incl. `modulating`/`ambiguous`) com o
  total de divergências visível, sem linguagem de acerto/erro do detector

### Requirement: Auditoria anti-drift da worklist de centro

O sistema SHALL fornecer `scripts/audit_center_adjudication.py` (molde de
`audit_tritone_adjudication.py`) que re-deriva as músicas `diverge` da extração corrente e verifica
que **toda** divergência está adjudicada e que não há veredito órfão (para música que não diverge
mais). A auditoria SHALL sair com código não-zero em qualquer discrepância.

#### Scenario: Divergência não-adjudicada acusa drift

- **WHEN** o corpus corrente tem uma música `diverge` sem entrada no corpus de adjudicação
- **THEN** a auditoria SHALL reportar a música faltante e sair com código não-zero

#### Scenario: Corpus alinhado à worklist passa

- **WHEN** toda música `diverge` tem veredito e todo veredito aponta para uma música ainda
  `diverge`
- **THEN** a auditoria SHALL sair com código zero e reportar a contagem por `winner`
