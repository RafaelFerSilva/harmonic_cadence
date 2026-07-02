## ADDED Requirements

### Requirement: Entradas resolvidas do ledger são aposentadas com proveniência

O sistema SHALL aposentar do ledger curado a entrada de uma música quarentenada quando sua
cifra é **recuperada da fonte** (re-transcrição do songbook original), com **registro da
resolução** (nota de proveniência no módulo do ledger: data e fonte da recuperação). Após a
recuperação, a auditoria local SHALL confirmar a ausência de divergência para o slug (o
vocabulário declarado pela fonte está contido na extração do arquivo novo), e a
materialização SHALL estampar a música como `complete`.

#### Scenario: Cifra re-transcrita sai da quarentena

- **WHEN** uma música `incomplete` é re-transcrita da página do songbook e o vocabulário dos
  diagramas do livro está contido na extração do arquivo novo
- **THEN** sua entrada SHALL ser removida do ledger (com nota de proveniência) e o próximo
  `corpus build` SHALL estampá-la `complete`

#### Scenario: Auditoria confirma a resolução

- **WHEN** `audit_completeness.py` roda após a recuperação
- **THEN** o slug recuperado SHALL NOT aparecer nem como divergência auditada nem como
  entrada de ledger sem suporte
