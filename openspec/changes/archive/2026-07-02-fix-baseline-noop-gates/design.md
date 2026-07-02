## Context

`songbook_baseline.py` afirma 4 invariantes "duros" born-green. Descoberto em
`persist-analysis-corpus`: 2 deles (**trítono**, **diminuto**) **não executam** — chamam
`Chord.get_category()` e `tgt.bass`, inexistentes em `domain/chord.py` (que expõe `.quality`,
`.properties.bass`), dentro de `try/except: continue`. O "170/170 verde" é vacuoso.

Rodando a checagem correta: **diminuto = 0** (invariante real), **trítono = 944** flags em
155/170. Recorte estrutural das 944: **425** = I7-como-tônica (`→T`, grau `I`, root==tônica;
legítimo, `i7-funk-anchor`); **~519** = `→T` em VI/III (T-por-grau, provável bug), `→Emp`
(backdoor/ambíguo), `→Outro` (não-classificado) — exigem adjudicação Chediak página-a-página.

## Goals / Non-Goals

**Goals:**
- Fazer os gates de trítono/diminuto **executarem** (corrigir os acessores).
- Diminuto vira **gate executável verde** (0 violações), endurecendo o baseline.
- Isentar a classe limpa I7-tônica (425) do ledger de trítono, citando `i7-funk-anchor`.
- Afiar o ledger de trítono para ~519 (baseline + `v_ledger_tritone_nondominant`).
- Sincronizar AGENTS.md/ROADMAP com o estado real.

**Non-Goals:**
- **Não** adjudicar os ~519 caso-a-caso (precisa do livro; não se cita o que não se tem).
- **Não** transformar trítono em gate verde (não é invariante limpo no corpus).
- **Nenhuma** mudança no motor de análise (`domain/`) — só a camada de validação + ledger.

## Decisions

### D1 — Corrigir os acessores, não reintroduzir a API fantasma
`_dominant_invariant`/`_diminished_invariant` passam a usar `Chord(sym).quality` (existe);
`_d2_resolution_invariant` passa a usar `tgt.properties.bass` (existe). **Não** adiciono
`Chord.get_category()`/`.bass` — seria manter a ilusão de uma API que o domínio não tem; a
fonte de qualidade é `.quality` (deriva de `parsed.category().value`). *Alternativa:* expor
`get_category()` no `Chord` — rejeitada (duplica `.quality`, superfície redundante).

### D2 — Isenção I7-tônica é estrutural e reusa a citação existente
Um acorde de trítono lido como `T` **com grau `I`** (root==tônica) é I7-como-tônica — Chediak
via `i7-funk-anchor` (Aquele Abraço). A guarda no ledger é `NOT (function_code=='T' AND
degree_base=='I')`: transposição-invariante (grau, não tom), sem precisar de `detect_key` (o
`degree` já vem da análise). Filtra exatamente os 425. *Alternativa:* comparar root_pc ==
tônica-pc — equivalente, mas exige aritmética de pitch-class na view; grau `I` é mais simples e
idêntico em efeito.

### D3 — Trítono é LEDGER, diminuto é GATE
Diminuto (0) vira gate executável que **falha** o build em violação. Trítono (~519 pós-isenção)
**não** é gate — é ledger/worklist reportado, coerente com `persist-analysis-corpus` (D9). O
`songbook_baseline.py` reframe a seção de trítono de "gate born-green" para "ledger de curadoria
(pós-isenção I7)".

### D4 — A view de ledger e o baseline aplicam a MESMA isenção
`v_ledger_tritone_nondominant` ganha `AND NOT (o.function_code='T' AND o.degree IN ('I','i'))`;
o baseline aplica a guarda equivalente em Python. Mantém as duas expressões alinhadas (o
princípio de paridade da change anterior).

## Risks / Trade-offs

- **[Isenção I7 esconde um bug real]** → a guarda é cirúrgica (grau `I` + `T`); um dominante
  secundário nunca tem grau `I` (grau reflete a posição da root na tônica), então V7/x não é
  isentado. Os `→T` em VI/III (167) permanecem no ledger.
- **[Baseline deixa de ser "tudo verde"]** → é o ponto: o verde era falso. Diminuto/D2/cadência
  seguem verdes reais; trítono passa a reportar ~519 honestos (worklist), não 0 fictício.
- **[~519 sem dono]** → documentados como worklist explícita (não silenciados); reabrem quando
  houver autoridade citável (Chediak página-a-página).

## Open Questions

- Alguns `→Emp` grau VII podem ser backdoor dominants legítimos (bVII7). Fica no ledger até
  adjudicação citada — não exemptar por ora (conservador).
