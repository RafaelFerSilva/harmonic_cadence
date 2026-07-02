## Context

Auditoria de completude (conversa de 2026-07-02, pós `fix-glued-chord-density`):
- **v4 (oráculo forte):** o songbook v4 (`songbook-v4-v2.md`, local/gitignored) declara o
  vocabulário por música (`**Acordes:**` + página) fora do fence. 16 músicas têm acordes
  declarados ausentes **como substring** do corpo — truncamento na conversão PDF→MD, anterior
  ao `split_songbook.py`. Irrecuperável sem a fonte original.
- **Originais (oráculo fraco):** manifesto `Acordes Utilizados` independente (veio da fonte);
  pós-fix os resíduos encolheram (dindi: só `D7(13)`) — precisa re-auditoria para a lista
  final, descontando dialeto (`C9`≈`C7(9)`, `FO`≈`F°`).
- **v3 (sem oráculo):** fonte deletada, manifesto gerado do corpo — ponto cego declarado.

Padrão a espelhar: `harmonic_analysis/corpus/modal_centers.py` (fato curado tipado, citação
obrigatória com falha rápida, fronteira de copyright = só fatos).

## Goals / Non-Goals

**Goals:**
- Ledger curado versionado de completude (fatos citáveis, sem texto de cifra).
- Auditoria local re-derivável que confere o ledger (anti-drift).
- `song.completeness` estampado na materialização; visibilidade no report.

**Non-Goals:**
- Recuperar conteúdo perdido (impossível sem fontes) ou re-converter PDFs.
- Filtrar gates duros (invariante por ocorrência vale em cifra parcial).
- Remover músicas do corpus (quarentena anota, não deleta — os acordes presentes são dado
  válido para invariantes e vocabulário).

## Decisions

### D1 — Ledger curado em código tipado, não tabela no banco
`completeness.py` espelha `modal_centers.py`: `@dataclass(frozen=True)` com
`CompletenessEvidence` obrigatória (`source` não-vazio; `missing_declared` não-vazio) e
`__post_init__` que falha na importação. O banco é derivado/regenerável — um fato curado não
pode morar só nele; vive no repo, versionado, e a materialização o **estampa**.
*Alternativa:* tabela curada no DuckDB — rejeitada (banco nunca é fonte de verdade).

### D2 — Dois status, honestos quanto à força da evidência
`incomplete` = oráculo do livro (v4 `Acordes:`) confirma ausência; `suspect` = manifesto
independente diverge sem fonte para confirmar. Ausente do ledger = `complete` (default). O v3
não entra (sem oráculo ≠ suspeito de graça — não inventar quarentena sem evidência).

### D3 — Auditoria é verificação, não geração cega
`audit_completeness.py` re-deriva declarado×extraído (com a extração ATUAL — os números movem
quando a extração melhora, como no fix-glued) e compara com o ledger: entrada curada sem
suporte na auditoria OU divergência auditada sem entrada viram avisos. O curador decide (pode
haver dialeto que a auditoria não desconta); o script mantém o ledger honesto. Precisa de
`cifras/` (e da fonte v4 se presente); sem eles, sai com aviso, não erro — é ferramenta local.

### D4 — Estampagem por slug na materialização; coluna, não tabela
`song.completeness TEXT NOT NULL DEFAULT 'complete'`; `materialize.py` consulta o ledger por
slug. Sem migração (banco regenerável). Report: seção 1 ganha a contagem por status; a seção 6
(worklist de trítono) marca padrões cujos exemplos venham de músicas quarentenadas — a
adjudicação sabe o que é parcial.

### D5 — Dialeto é descontado ANTES de curar
A auditoria desconta: (a) token colado/decoração (já resolvido pelo fix); (b) equivalência de
grafia simples via parse (`C9` e `C7(9)` têm mesmos pitch-classes → não é ausência);
(c) mojibake conhecido (`FO`≈`F°`). O que sobra é candidato a fato — o curador confirma antes
de entrar no ledger.

## Risks / Trade-offs

- **[Ledger desatualiza quando a extração melhora]** → D3: a auditoria roda contra a extração
  corrente e acusa divergência; re-curar é barato (lista pequena).
- **[Falso `incomplete` por dialeto no header do livro]** (`B74(9)`, `E74` são grafias do
  songbook) → D5 + curadoria manual: só entra no ledger o que sobreviver ao desconto; o
  design aceita que alguns "1 acorde ausente" fiquem FORA do ledger na dúvida (conservador:
  quarentena exige evidência, não suspeita fraca).
- **[Quarentena lida como defeito do motor]** → linguagem: `completeness` é qualidade do DADO
  de entrada, não da análise; report a apresenta na seção de corpus, não como erro.

## Migration Plan

Aditivo. `corpus build` novo estampa a coluna; bancos antigos regeneram. Rollback = remover
módulo/script/coluna.

## Open Questions

- Nenhuma bloqueante. (A lista final de `suspect` sai da re-auditoria na implementação.)
