## Why

A auditoria de completude (2026-07-02) provou que parte do corpus analisa **cifras
incompletas**: **16 músicas do songbook v4** perderam seções na conversão PDF→MD (oráculo: o
header `Acordes:` do próprio livro declara acordes que o corpo não contém nem como substring —
ex.: A paz sem a seção em modo menor, Tempo feliz com 4-5 de 14 acordes declarados ausentes) e
**~13 cifras originais** têm manifesto independente divergente (re-auditar pós
`fix-glued-chord-density`, que encolheu os resíduos). Hoje nada distingue dado completo de dado
parcial: a corroboração de centro, o ledger de trítono e as analytics tratam uma cifra pela
metade como música inteira — contaminando exatamente as worklists que a adjudicação Chediak vai
consumir. O conteúdo perdido é irrecuperável sem as fontes; o que se pode (e deve) fazer é
**quarentenar com evidência**.

## What Changes

- **Ledger curado de completude** (`harmonic_analysis/corpus/completeness.py`), no padrão do
  `modal_centers`: fatos tipados `{slug, status, missing_declared, evidence}` com **evidência
  obrigatória** (`__post_init__` falha rápido) — só FATOS (slug + símbolos de acorde ausentes +
  fonte da evidência), nunca texto de cifra (fronteira de copyright preservada). Status:
  `incomplete` (oráculo do livro confirma ausência) ou `suspect` (manifesto independente
  diverge, sem fonte para confirmar).
- **Script de auditoria local** (`scripts/audit_completeness.py`): re-deriva a evidência
  (declarado × extraído sobre `cifras/*.md` + header `Acordes:` da fonte v4 quando presente,
  descontando dialeto/colados) e **confere o ledger curado** — divergência ledger×auditoria é
  reportada, mantendo o ledger honesto e regenerável-verificável.
- **Coluna `completeness`** na tabela `song`, estampada do ledger na materialização
  (`complete` por default); o **`corpus report`** ganha visibilidade (contagem por status na
  seção 1 e marcação nas worklists de curadoria).
- **Gates duros NÃO filtram**: o invariante por ocorrência (diminuto, D2, cadência) vale em
  cifra parcial — cada acorde presente continua tendo que obedecer Chediak. A quarentena é
  metadado de **curadoria** (centro, adjudicação de trítono), não de validação funcional.

## Capabilities

### New Capabilities
- `corpus-completeness`: ledger curado de completude com evidência obrigatória, auditoria
  local que o verifica, estampagem na persistência e visibilidade no relatório.

### Modified Capabilities
<!-- Nenhuma modificação de requisito existente: os gates não mudam; a coluna nova e a seção
     de relatório são aditivas dentro da capability nova. -->

## Impact

- **Código:** novo `harmonic_analysis/corpus/completeness.py` (curado, versionado); novo
  `scripts/audit_completeness.py` (local, precisa de `cifras/`); `persistence/schema.sql`
  (+coluna `completeness` em `song`), `materialize.py` (estampa), `report.py` (visibilidade).
- **Banco:** regenerável — `corpus build` novo estampa; bancos antigos não migram (regenera).
- **Sem impacto no motor** nem nos gates; baseline (`songbook_baseline.py`) intocado.
- **Curadoria:** worklists de centro/trítono passam a saber o que é dado parcial — insumo mais
  honesto para a adjudicação Chediak.
