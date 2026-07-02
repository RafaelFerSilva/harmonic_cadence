## Context

Fontes em `songbooks/` (5 volumes PDF, gitignored). Vol. 4: **offset PDF = página do livro −
20** (calibrado: PDF 120 = livro 140), scan legível com diagramas de acorde no topo (o
vocabulário declarado pelo livro) + cifra acordes-sobre-letra. As 15 páginas das cifras
`incomplete` são conhecidas (p.32-150 do livro). Probe (tempo-feliz, livro p.142/PDF 122)
provou corrupção além de truncamento: tonalidade trocada e conteúdo divergente.

## Goals / Non-Goals

**Goals:**
- 15 cifras re-transcritas do livro (tom impresso, acordes+letra, manifesto dos diagramas).
- Verificação mecânica por música (extração ⊇ diagramas) + auditoria sem drift.
- Ledger: 15 `incomplete` aposentadas com proveniência; re-medição completa.

**Non-Goals:**
- Não auditar as demais ~36 do v4 contra o livro (a corrupção pode existir fora das 15 — o
  oráculo só pega ausência de vocabulário; fica REGISTRADO como risco/possível change futura).
- Não tocar as 13 `suspect` (originais; outro oráculo).
- Não ingerir Vols. 1/2/5 (é a frente #8, change própria).

## Decisions

### D1 — Re-transcrever, não remendar
A corrupção provada (transposição + conteúdo alterado) invalida o patch incremental. Fonte =
página do livro; o arquivo novo substitui o velho integralmente, no TOM IMPRESSO. O formato
segue o padrão do corpus (`## <a name=…>`, compositores, `Acordes Utilizados` = diagramas da
página, bloco ``` com acordes alinhados sobre a letra).

### D2 — Verificação mecânica antes de aceitar cada transcrição
Para cada música: `extract_chords_from_lines(arquivo novo) ⊇ diagramas do livro` (mesmo
critério da quarentena, agora com a fonte na mão). Diagramas transcritos junto com a página.
Diferenças de grafia (ex.: `D6/9` vs `D%`) resolvidas a favor da grafia canônica do projeto.

### D3 — Aposentadoria com proveniência no ledger
As 15 entradas saem de `_INCOMPLETE`; o docstring do `completeness.py` ganha um changelog
curto ("2026-07-02: 15 v4 re-transcritas da fonte, PDF Vol.4"). A auditoria
(`audit_completeness.py`) valida: sem drift = as 15 não acusam mais. Registro também no
`TRITONE-ADJUDICATION.md`? Não — arquivo próprio é exagero; AGENTS.md resume.

### D4 — Transcrição em lotes com páginas duplas
Ler 2-4 páginas por vez (algumas cifras ocupam 2 páginas — conferir continuação antes de
fechar o arquivo); transcrever com atenção a: repetições (`%`, `./.`), acordes colados de
diagrama, seções (a página às vezes traz partitura ao pé — ignorar, só cifra+letra).

## Risks / Trade-offs

- **[Erro de transcrição meu]** → mitigado por D2 (vocabulário fecha com os diagramas) +
  baseline (gates duros pegariam incoerência funcional grosseira).
- **[Corrupção nas outras ~36 do v4]** → fora de escopo, registrado; o oráculo de vocabulário
  não a detecta quando o vocabulário fecha. Auditoria ampla v4×livro é candidata a change.
- **[Centro/estatísticas mudam]** → esperado: o tom passa a ser o do livro. A análise
  funcional é transposição-invariante; gates re-medidos.

## Migration Plan

Dados locais (gitignored) + ledger. Rollback = restaurar cifras antigas (ficam em backup
local `cifras/.bak-<data>/` durante a change) e reverter o ledger.

## Open Questions

- Nenhuma bloqueante.
