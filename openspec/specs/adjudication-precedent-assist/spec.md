# adjudication-precedent-assist

## Purpose

Assistência de adjudicação por precedente: dado um caso suspeito (ledger de trítono
ou worklist de centro), recupera os vereditos **confirmados por humano** mais próximos
por **geometria harmônica transposição-invariante** e emite um veredito **DRAFT** com
citação herdada e confiança visível. Estritamente PRATA/aditivo — o draft nunca conta
como adjudicação confirmada (só o humano promove); não altera `function_code`, `degree`,
`detect_key`, gates duros nem o placar de corroboração de centro.

## Requirements

### Requirement: Vetor de geometria harmônica transposição-invariante

O sistema SHALL derivar, para uma ocorrência de acorde suspeita, um vetor de
características de **função/intervalo** (função, grau, qualidade, intervalo
raiz→tônica, intervalo de resolução ao próximo acorde) a partir do `corpus.duckdb`,
sem usar o tom absoluto. Duas ocorrências idênticas a menos de transposição SHALL
produzir o mesmo vetor.

#### Scenario: Mesma geometria em tons diferentes
- **WHEN** duas ocorrências têm a mesma função, grau, qualidade e os mesmos
  intervalos raiz→tônica e de resolução, mas em tons diferentes
- **THEN** o vetor de geometria das duas é idêntico e a distância entre elas é 0

#### Scenario: Ocorrência inexistente falha visível
- **WHEN** o `(slug, position)` pedido não existe no corpus
- **THEN** o sistema falha com erro explícito (slug/posição não encontrado), sem
  produzir vetor silenciosamente vazio

### Requirement: Retrieval de precedente sobre vereditos confirmados

O sistema SHALL recuperar, para uma ocorrência suspeita, os `k` casos mais próximos
**exclusivamente** entre os vereditos **confirmados por humano** dos corpora tipados
(`tritone_adjudications`, `tonal_center_adjudications`), ordenados por distância de
geometria crescente. A própria ocorrência, se já adjudicada, SHALL ser excluída dos
vizinhos (sem auto-precedente).

#### Scenario: Top-k por distância crescente
- **WHEN** o usuário pede assistência para uma ocorrência com `--k N`
- **THEN** o sistema retorna até `N` precedentes confirmados, ordenados por distância
  crescente, sem incluir a própria ocorrência

#### Scenario: Base de precedentes só confirmados
- **WHEN** existe um veredito ainda `draft` (não promovido) para outra ocorrência
- **THEN** esse draft NÃO aparece como precedente (só vereditos confirmados por humano
  entram na base de casos)

### Requirement: Veredito DRAFT com citação herdada e confiança visível

O sistema SHALL emitir um veredito **DRAFT** para a ocorrência suspeita, com
`status="draft"`, cujo `verdict kind` e `Citation` são **herdados do precedente mais
próximo**, e cuja confiança é a **fração dos `k` precedentes que concordam** com esse
`verdict kind` (denominador `k` visível). O draft SHALL ser marcado explicitamente como
**não-confirmado**.

#### Scenario: Citação herdada, nunca extraída do livro
- **WHEN** o precedente mais próximo é `chromatic_approach` com `Citation` p.116
- **THEN** o draft recebe `verdict="chromatic_approach"` e a MESMA citação p.116,
  herdada do precedente confirmado — nunca extraída do texto/PDF do Chediak

#### Scenario: Confiança por concordância dos vizinhos
- **WHEN** dos `k=5` precedentes, 4 concordam com o veredito do mais próximo
- **THEN** a confiança reportada é 4/5 com o denominador visível

#### Scenario: Precedente ambíguo gera draft ambíguo sem citação
- **WHEN** o precedente mais próximo é `ambiguous`
- **THEN** o draft é `ambiguous` (sem citação, com a nota geométrica do precedente),
  refletindo honestamente a indecisão — nunca forçado a um veredito decisivo

### Requirement: Draft nunca conta como adjudicação confirmada

O sistema SHALL manter os drafts **estritamente separados** do corpus confirmado. Um
draft NUNCA SHALL ser tratado como veredito adjudicado por nenhum consumidor: os
scripts `audit_tritone_adjudication.py`/`audit_center_adjudication.py` e o denominador
de completude SHALL ignorar drafts; só o humano promove um draft a veredito confirmado.

#### Scenario: Auditoria anti-drift ignora drafts
- **WHEN** existem drafts materializados e o `audit_*_adjudication.py` roda
- **THEN** a auditoria de completude reporta o mesmo resultado que reportaria sem
  drafts (drafts fora do denominador; nenhum "veredito órfão" a menos)

#### Scenario: Invariante PRATA preservado
- **WHEN** o motor de precedente roda sobre o corpus
- **THEN** nenhum `function_code`, `degree`, veredito confirmado, gate duro ou
  `detect_key` é alterado (a saída é aditiva)

### Requirement: Relatório `harmonic corpus assist`

O sistema SHALL expor `harmonic corpus assist [--occurrence <slug>:<pos>] [--k N]
[--ledger tritone|center]` que produz um relatório Markdown em PT-BR contendo: a
ocorrência suspeita e sua geometria, os top-`k` precedentes (símbolo, veredito,
citação, distância) e o veredito DRAFT com a confiança e o **flag não-confirmado**.
Sem `--occurrence`, o comando SHALL varrer as ocorrências do ledger ainda **sem
veredito humano** e listar um draft por ocorrência.

#### Scenario: Assistência de uma ocorrência
- **WHEN** `harmonic corpus assist --occurrence flora:12 --ledger tritone`
- **THEN** o relatório mostra a geometria de `flora:12`, os precedentes confirmados
  mais próximos com citação, e um veredito DRAFT marcado não-confirmado

#### Scenario: Varredura da worklist pendente
- **WHEN** `harmonic corpus assist --ledger center` sem `--occurrence`
- **THEN** o relatório lista um draft por ocorrência de centro `diverge` ainda sem
  veredito humano, com denominador visível

### Requirement: Materialização aditiva `v_draft_verdict`

O sistema SHALL materializar os drafts numa view aditiva `v_draft_verdict` (derivada e
regenerável; rollback por `DROP VIEW`), sem tocar `schema.sql`/`views.sql` das tabelas
canônicas. A view SHALL expor a ocorrência, o `verdict kind` do draft, a confiança, a
citação herdada e o `status="draft"`.

#### Scenario: Rollback limpo
- **WHEN** a view `v_draft_verdict` é removida (`DROP VIEW`)
- **THEN** o corpus e os gates permanecem íntegros, sem resíduo (a view é puramente
  derivada)

### Requirement: Candidatos à armadilha ii-V como ranking PRATA

Quando o ranking de armadilha ii-V for solicitado, o sistema SHALL listar as
ocorrências candidatas (o `detect_key` aponta o V e o `chediak_functional_center`
aponta o ii de um mesmo alvo) além dos 3 casos já conhecidos, como sugestão PRATA para
curadoria. Esse ranking NÃO SHALL alterar `detect_key` nem o placar de corroboração de
centro.

#### Scenario: Candidatos além dos 3 conhecidos
- **WHEN** o ranking de armadilha ii-V é solicitado
- **THEN** o sistema lista os 3 conhecidos (`bolinha-de-sabao`/`menina`/`rio`) e
  quaisquer novos candidatos, marcados como sugestão PRATA, sem tocar `detect_key`
