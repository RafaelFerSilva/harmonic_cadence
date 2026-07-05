# Proposal — ingest-songbook-vols-2-5

## Why

A frente #8 pede ampliar o corpus baseline com os volumes do Songbook Bossa Nova ainda
ausentes. O probe read-only desta change corrigiu o mapa: **o Vol. 1 (62 músicas) JÁ É o
corpus original n=62** (interseção de slugs 12/12 conferida contra o índice do livro) — a
frase "Vols. 1/2/5 nunca ingeridos" do AGENTS.md está errada quanto ao Vol. 1. O que falta
de verdade são os **Vols. 2 (~62 músicas) e 5 (63 músicas)**, confirmados ausentes
(aguas-de-marco, ana-luiza, berimbau, desafinado, garota-de-ipanema… nenhum no corpus).
As fontes estão em `songbooks/` (PDF, gitignored) e o protocolo de transcrição assistida
página-a-página foi provado na `retranscribe-v4-quarantined` — a conversão automática
PDF→MD foi a origem de TODA a corrupção do v4 e está descartada.

## What Changes

- **Ingestão de ~125 músicas novas** (Vols. 2 e 5) em `cifras/<slug>.md`, transcritas do
  PDF no **tom impresso**, formato padrão do corpus (header + `Acordes Utilizados:` =
  diagramas da página + fence com acordes sobre letra). Corpus **170 → ~295**.
- **Verificação mecânica por música** (o oráculo forte da quarentena, agora na admissão):
  `extract_chords_from_lines(arquivo novo) ⊇ diagramas do livro`. Grafias empilhadas do
  livro (`B6/9` como fração, `E7(4)(9)`, `A(add9)/E`) normalizadas à grafia canônica do
  projeto. Nenhuma música entra sem passar.
- **Correção de fato nos docs**: AGENTS.md/ROADMAP.md deixam de dizer que o Vol. 1 nunca
  foi ingerido; registram a proveniência real (conversão antiga, mesma família lossy do
  v4) e o risco Vol.1×livro na frente de auditoria ampla.
- **Re-medição completa**: `audit_completeness.py` sem drift; `songbook_baseline.py` com
  os 3 gates duros verdes no denominador novo (~295/~295 — política pausa-e-investiga);
  `harmonic corpus build/gates/report` (A/B com o run anterior). Ledger de trítono e
  corroboração de centro ganham números novos (dado novo, não regressão).

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `corpus-completeness`: ganha o requisito de **admissão verificada da fonte primária** —
  uma cifra nova transcrita do livro só entra no corpus após a verificação de vocabulário
  (extração ⊇ diagramas da página), entra como `complete`, e a auditoria não a acusa;
  colisão de slug com arquivo existente nunca sobrescreve (colisão = investigar).

## Impact

- **Dados (gitignored):** ~125 arquivos novos em `cifras/`; backup `cifras/.bak-<data>/`
  durante a change. `songbooks/` intocado (fonte de leitura).
- **Código:** nenhuma mudança de motor/extração. Possível utilitário de verificação de
  lote (reuso do critério do `audit_completeness.py`).
- **Docs (no repo):** AGENTS.md, ROADMAP.md (fato do Vol. 1 + números novos). Copyright
  preservado: só fatos entram no repo; cifras e PDFs seguem gitignored.
- **Calibração conhecida:** Vol. 2 — offset PDF = página do livro − 25; PDF cortado (sem
  índice próprio) → enumeração pelo índice-irmão impresso no Vol. 1 + varredura alfabética.
  Vol. 5 — índice próprio com páginas (livro ~pp.28–160; entradas borradas recuperáveis na
  varredura; o número impresso é a autoridade, não a ordem alfabética); offset a calibrar
  no início do apply.
- **Fora de escopo:** auditoria Vol. 1/3/4 × livro (change futura; risco registrado); as
  13 `suspect`; Camada C.
