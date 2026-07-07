## MODIFIED Requirements

### Requirement: Consulta de famílias na CLI

O sistema SHALL expor `harmonic corpus clusters [--k N]` que lista, por família: o tamanho, a
música-protótipo, os membros e os **traços harmônicos salientes por CONTRASTE** que a definem. Um
traço saliente é uma função ou família de cadência **sobre-representada** na família em relação à
média do corpus (lift = participação média na família − participação média no corpus > 0), ordenada
por lift decrescente, com o valor do lift **visível**. Quando uma família não tem nenhum traço acima
da média, o sistema SHALL sinalizar isso explicitamente (ela É o baseline do corpus), em vez de
listar funções comuns. A saída SHALL ser descritiva; NÃO SHALL apresentar as famílias como veredito
de qualidade ou correção — família é uma relação descritiva entre músicas.

#### Scenario: Traços por contraste distinguem a família

- **WHEN** o usuário roda `corpus clusters --k N`
- **THEN** cada família mostra as funções/cadências sobre-representadas em relação ao corpus (lift > 0), com o valor do lift visível

#### Scenario: Família-baseline é sinalizada

- **WHEN** uma família não tem nenhuma função/cadência acima da média do corpus
- **THEN** a saída sinaliza que a família é o baseline do corpus (sem inventar traços distintivos)

#### Scenario: Descritivo, nunca placar

- **WHEN** a saída é gerada
- **THEN** ela NÃO contém vocabulário de placar (acurácia/qualidade da família como verdade)
