# Design — ingest-songbook-vols-2-5

## Context

Fontes em `songbooks/` (5 PDFs, gitignored). Probe read-only desta change:

- **Vol. 1** = corpus original n=62 (fato novo; corrige AGENTS/ROADMAP). Auditoria
  Vol.1×livro é OUTRA change.
- **Vol. 2** (~62 músicas pelo índice-irmão impresso no Vol. 1): PDF **cortado** — sem
  front matter/índice próprio; começa no miolo. **Offset calibrado: PDF = página do livro
  − 25** (PDF 3 = livro 28; Águas de março livro p.30 = PDF 5). Scan legível; formato
  padrão Chediak (título/compositor, diagramas no topo, cifra acordes-sobre-letra,
  partitura ao pé).
- **Vol. 5** (63 músicas declaradas): índice próprio com números de página (livro
  ~pp.28–160; PDF pp.3–4), com manchas de tinta sobre algumas entradas; ordem do índice
  tem exceções (Duas contas p.83) — **o número de página impresso é a autoridade**.
  Offset a calibrar na 1ª página de música do apply.

Protocolo de transcrição provado na `retranscribe-v4-quarantined` (15/15 verificadas).
A conversão automática PDF→MD está descartada (origem de toda a corrupção do v4:
transposição espúria, páginas perdidas, OCR mangling).

## Goals / Non-Goals

**Goals:**
- ~125 cifras novas (Vols. 2 e 5) transcritas do livro no tom impresso, verificadas por
  vocabulário, corpus 170→~295.
- Enumeração honesta por volume (worklist explícita; músicas não-encontradas/ilegíveis
  reportadas, nunca silenciadas).
- Re-medição completa + correção do fato do Vol. 1 nos docs.

**Non-Goals:**
- Auditar Vols. 1/3/4 contra o livro (risco registrado; change futura).
- Tocar as 13 `suspect`, o motor, a extração ou o ledger de trítono (números novos são
  re-medição, não re-adjudicação).

## Decisions

### D1 — Transcrição assistida página-a-página; conversão automática proibida
O modelo lê o PDF direto (2–4 páginas por vez; cifras de 2 páginas conferidas antes de
fechar o arquivo). Alternativa rejeitada: OCR/conversão em massa — foi exatamente o que
corrompeu o v4, e a corrupção que importa (transposição espúria) é invisível ao oráculo
de vocabulário.

### D2 — Enumeração por volume com worklist explícita
- **Vol. 2:** lista-alvo do índice-irmão (Vol. 1, PDF pp.4–5, sem páginas) + varredura
  sequencial do PDF com o offset −25; cada música encontrada é riscada da lista. Sobras
  (na lista e não no PDF, ou vice-versa) viram fatos reportados na change.
- **Vol. 5:** mapa página→música do índice próprio; entradas borradas recuperadas pela
  varredura. Divergência índice×miolo: o miolo (página impressa) decide.

### D3 — Verificação mecânica na ADMISSÃO (o oráculo forte vira gate de entrada)
Para cada música, antes de aceitar: `extract_chords_from_lines(arquivo) ⊇ diagramas da
página`. Mesmo critério da quarentena/re-transcrição, agora preventivo. Diferenças de
grafia resolvidas a favor da grafia canônica do projeto (`B6/9` empilhado → `B6(9)`;
sufixos conforme `cifra_core.theory.chord_parse`). Diagramas transcritos junto com a
página — o manifesto `Acordes Utilizados:` é o vocabulário que o livro declara, não o
extraído (senão a verificação seria circular).

### D4 — Lotes com medição intermediária
Lotes de ~10–15 músicas; após cada lote, verificação de vocabulário do lote; baseline
completo ao fim de cada volume. Política pausa-e-investiga: gate duro quebrado =
investigar a transcrição/dado (erro de transcrição é a hipótese nº 1), nunca forçar
verde nem "consertar" o motor no meio da ingestão.

### D5 — Colisão de slug nunca sobrescreve
`cifras/<slug>.md` existente + música homônima no Vol. 2/5 = parar e investigar (pode ser
repertório repetido entre volumes ou colisão de slugify). Se for a mesma música em
arranjo/volume diferente, decisão registrada (esperado: manter a existente e reportar; a
troca de arranjo seria curadoria, não ingestão). Backup `cifras/.bak-<data>/` antes do
primeiro write.

### D6 — Completude estampada como `complete`
As ~125 entram fora de qualquer quarentena (verificadas na admissão);
`audit_completeness.py` deve fechar sem drift sobre o corpus ampliado. O manifesto do
header é o oráculo futuro da auditoria — por isso ele vem dos diagramas do livro (D3).

## Risks / Trade-offs

- **[Erro de transcrição meu]** → D3 (vocabulário fecha com os diagramas) + gates duros no
  baseline (incoerência funcional grosseira aparece) + tom impresso conferido na página.
- **[Scan ilegível em páginas do Vol. 5]** → worklist honesta: música ilegível NÃO entra,
  fica listada como pendência com página (sem oráculo não há admissão — nada de chutar).
- **[Índice-irmão do Vol. 2 desatualizado]** (impresso na 2ª ed. do Vol. 1) → a varredura
  sequencial é a verdade; o índice é só checklist de cobertura.
- **[Denominador novo mexe nos números]** → esperado e desejado: gates duros devem seguir
  100%; ledger de trítono e centro ganham casos novos que são INSUMO das frentes de
  adjudicação, não defeito desta change.
- **[Esforço grande (~125 músicas × 1–2 páginas)]** → lotes (D4) tornam a change
  interrompível/retomável sem estado perdido: o corpus em disco + worklist riscada são o
  checkpoint.

## Migration Plan

Dados locais (gitignored) + docs. Rollback = restaurar `cifras/.bak-<data>/` e reverter
os docs. Nenhuma migração de código/banco (o DuckDB é regenerável por `corpus build`).

## Open Questions

- Nenhuma bloqueante. (Offset do Vol. 5 e entradas borradas do índice se resolvem nas
  primeiras páginas do apply, por construção.)
