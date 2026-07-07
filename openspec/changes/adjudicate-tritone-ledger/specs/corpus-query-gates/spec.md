## MODIFIED Requirements

### Requirement: Trítono não-dominante é ledger de curadoria, não gate

O sistema SHALL tratar a leitura trítono-real-não-dominante como ledger de curadoria, não como
gate que falha o build. O invariante "todo trítono real ⇒ função dominante" **não é** um
invariante limpo no corpus:
o motor lê legitimamente muitos acordes de trítono real como `T` (tônica `I7` de blues/funk,
cf. `i7-funk-anchor`) ou `Emp` (empréstimo modal). Portanto o sistema SHALL expor a leitura
trítono-real-não-dominante como um **ledger de curadoria** (worklist a adjudicar por Chediak),
**não** como gate que falha o build. O comando `corpus gates` SHALL reportar a contagem do
ledger de forma informativa, sem sair com erro por causa dele. A view
`v_ledger_tritone_nondominant` SHALL, além de identificar cada ocorrência, expor o **veredito
adjudicado** e a **página Chediak citada** quando a ocorrência já foi adjudicada (via corpus
`tritone-adjudication`), mantendo-se informativa e aditiva (rollback = reverter a view).

#### Scenario: Ledger de trítono é informativo, não bloqueante

- **WHEN** `corpus gates` roda sobre o corpus atual (que contém acordes de trítono real lidos
  como `T`/`Emp`)
- **THEN** o comando SHALL imprimir a contagem de ocorrências trítono-real-não-dominante como
  worklist de curadoria, e SHALL NOT sair com erro por causa dessas ocorrências (só os gates
  executáveis bloqueiam).

#### Scenario: Ledger identifica cada ocorrência e seu veredito

- **WHEN** a view `v_ledger_tritone_nondominant` é consultada
- **THEN** ela SHALL retornar, por ocorrência de trítono real cujo `function_code` não é
  dominante, o `song_id`, `position`, `symbol` e `function_code` — insumo de adjudicação, nunca
  placar de acerto/erro — E, quando a ocorrência já foi adjudicada, o `verdict` e a página
  Chediak citada; ocorrência ainda não adjudicada SHALL aparecer com veredito nulo (não some da
  view).
