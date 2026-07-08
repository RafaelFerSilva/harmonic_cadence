## Why

A adjudicação dos ledgers de curadoria — trítono não-dominante (43) e centro
`diverge` (46) — hoje é **100% manual** (curador + PDF do Chediak, leva a leva). O
`ML-EVOLUTION-PLAN.md` §5 e o `PROBE-EMBEDDINGS-FINDINGS.md` provaram ao vivo que a
via de Deep Learning não se paga aqui: os labels adjudicados (43+46=89,
desbalanceados) são pequenos demais para um classificador supervisado (decora, não
generaliza) e embeddings de acorde aprendidos **quebram a invariância de
transposição** (0.63–0.68 vs. ~1.0 do `Fingerprint` à mão) = NO-GO. A frente
neuro-simbólica que **sobrevive aos princípios do projeto** é o **retrieval de
precedente (case-based reasoning)**: reusar os vereditos já adjudicados como base de
casos, keados pela geometria harmônica (invariante a transposição), para *rascunhar*
— nunca decidir — o veredito de uma nova ocorrência suspeita, acelerando a próxima
rodada de adjudicação humana sem custo de dado novo nem dependência pesada.

## What Changes

- **Novo módulo `overlay/precedent.py`** — motor de CBR que, para uma ocorrência
  suspeita (do ledger de trítono ou da worklist de centro), extrai um **vetor de
  geometria harmônica** re-derivado do DuckDB (função, grau, intervalo raiz→tônica,
  intervalo de resolução, qualidade — features de FUNÇÃO/INTERVALO, **não de tom**) e
  recupera os `k` casos **já adjudicados por humano** mais próximos dos corpora
  tipados (`corpus/tritone_adjudications.py`, `corpus/tonal_center_adjudications.py`).
- **Veredito DRAFT** = o `verdict kind` + a `Citation` do precedente mais próximo,
  com a **concordância entre os `k`** como confiança visível, **marcado
  explicitamente como não-confirmado** (`status="draft"`). Um draft NUNCA conta como
  adjudicado; só o humano promove (o corpus confirmado permanece a única verdade).
- **CLI `harmonic corpus assist [--occurrence <slug>:<pos>] [--k N] [--ledger
  tritone|center]`** → relatório MD PT-BR: a suspeita + sua geometria, os top-`k`
  precedentes (símbolo, veredito, citação, distância), e o veredito DRAFT + confiança,
  com **flag não-confirmado** e **denominador visível**. Sem argumento de ocorrência,
  varre a worklist pendente (ocorrências do ledger ainda sem veredito humano).
- **View aditiva `v_draft_verdict`** (derivada/regenerável; rollback = DROP) — os
  drafts materializados. Os scripts `audit_*_adjudication.py` **continuam ignorando
  drafts** (só vereditos confirmados contam; anti-drift inalterado).
- **Sub-uso: candidatos à armadilha ii-V** — como o mesmo motor de geometria detecta o
  padrão "detect pega o V, funcional pega o ii", pode **rankear candidatos além dos 3
  conhecidos** (que o Path D codificou à mão) como sugestão PRATA para curadoria —
  sem tocar `detect_key`.
- **Fase 2 explicitamente ADIADA** (fora desta change): camada de LLM-drafting de
  vereditos citados em escala — só depois que a Fase 1 (CBR) provar o loop. Disciplina
  "medir antes de construir"; nenhuma dependência pesada na fé.

## Capabilities

### New Capabilities
- `adjudication-precedent-assist`: motor de retrieval de precedente sobre os corpora
  de adjudicação confirmados, produzindo vereditos DRAFT (não-confirmados) com citação
  herdada e confiança por concordância, expostos por `harmonic corpus assist` e pela
  view aditiva `v_draft_verdict`. Descritivo e subordinado ao símbolo (PRATA): rascunha
  para o humano, nunca arbitra.

### Modified Capabilities
<!-- Nenhuma. Os specs `tritone-adjudication` e `tonal-center-adjudication` definem os
     vereditos CONFIRMADOS por humano — permanecem a fonte de verdade e não mudam de
     requisito. Os drafts são uma camada aditiva e separada. -->

## Impact

- **Código novo:** `packages/harmonic_analysis/src/harmonic_analysis/overlay/precedent.py`
  (motor CBR) + wiring no `overlay/materialize.py` (view `v_draft_verdict`) e no
  `overlay/report.py`/CLI `corpus` (subcomando `assist`). Reusa `overlay/similarity.py`
  (a métrica de similaridade já testada) e os corpora tipados de `corpus/`.
- **Sem dependência nova:** retrieval sobre features simbólicas; o núcleo
  (`cifra_core`, `domain/`, `validation/`) segue **stdlib-puro**. Peso de overlay vive
  só em `overlay/` (lei de isolamento).
- **PRATA / invariantes intocados:** NUNCA reescreve `function_code`/`degree`, NUNCA
  arbitra centro, NUNCA toca os 3 gates duros nem `detect_key`. Medido ao vivo contra
  `songbook_baseline.py` — pausa-e-investiga se um gate quebrar (esperado: **293/293**
  inalterado, coder intocado).
- **Fronteira de copyright preservada:** o motor trabalha **só da geometria** (já no
  DuckDB) + do **precedente já adjudicado** — **não ingere o PDF do Chediak**. As
  citações são herdadas do precedente confirmado (fato já curado), nunca extraídas do
  texto do livro.
- **Avaliação anti-circularidade:** métrica **descritiva** = taxa de confirmação
  humana dos drafts (hold-out do curador), **nunca acurácia contra o coder**. Um draft
  refutado pelo humano é sinal do limite do CBR, não erro do corpus.
- **Anti-drift:** `audit_*_adjudication.py` inalterados (drafts fora do denominador de
  completude); um novo probe/teste garante que draft nunca vaza para o corpus confirmado.
