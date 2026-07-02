## Why

Os 5 volumes do Songbook Bossa Nova chegaram em `songbooks/` (PDF, gitignored — copyright).
O probe de viabilidade no Vol. 4 (offset PDF = página do livro − 20; scan legível) revelou que
a corrupção das 15 cifras em quarentena é **pior que truncamento**: `tempo-feliz.md` está em
tonalidade diferente do livro (arquivo em Sol, livro em Ré) e com conteúdo divergente que nem
transposição limpa explica (`D6` do livro viraria `G6`, o arquivo tem `C7M`) — a conversão
PDF→MD original **transpôs e alterou** conteúdo. Remendar seções não basta; a fonte agora é
legível diretamente, então o caminho honesto é **re-transcrever as 15 do livro**, página a
página, no tom impresso.

## What Changes

- **Re-transcrição das 15 cifras `incomplete`** direto do PDF do Vol. 4 (páginas conhecidas:
  livro p.32→PDF 12 … p.150→PDF 130), substituindo os `cifras/<slug>.md` corrompidos:
  acordes+letra alinhados como impressos, no TOM DO LIVRO, com o manifesto `Acordes
  Utilizados` derivado dos diagramas da página (o vocabulário que o próprio livro declara).
- **Verificação por música**: extração do arquivo novo ⊇ diagramas do livro (o oráculo da
  quarentena); `scripts/audit_completeness.py` deve parar de acusar as 15.
- **Ledger de completude atualizado**: as 15 saem de `incomplete` (removidas do
  `completeness.py` com nota no docstring — a quarentena cumpriu o papel e foi resolvida
  pela fonte).
- **Re-medição**: baseline (gates duros 170/170; centro pode mudar — os tons corrigidos são
  dado novo) + `corpus build`/`report` (A/B com o run anterior).
- A análise funcional é transposição-invariante por construção — corrigir o tom do arquivo
  NÃO deveria mudar graus/funções relativos, mas centros absolutos e vocabulário sim
  (esperado e desejado: o dado passa a ser o do livro).

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `corpus-completeness`: ganha o requisito de **aposentadoria com proveniência** — uma
  entrada do ledger resolvida pela fonte (cifra re-transcrita do livro) é REMOVIDA do
  ledger com registro da resolução (docstring/changelog do módulo), e a auditoria passa a
  confirmar a ausência de divergência para aquele slug.

## Impact

- **Dados:** 15 arquivos em `cifras/` (locais, gitignored) re-escritos da fonte;
  `corpus/completeness.py` (removidas as 15 entradas `incomplete`; ficam as 13 `suspect`).
- **Sem mudança de código de motor/extração** — só o ledger curado e os dados locais.
- **Números documentados** (AGENTS/relatório) atualizados na re-medição.
- **Copyright:** as cifras re-transcritas ficam em `cifras/` (gitignored, como sempre); no
  repo entram só fatos (ledger/números). `songbooks/` já está gitignored.
