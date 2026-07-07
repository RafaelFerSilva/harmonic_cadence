## Why

O `v_ledger_tritone_nondominant` tem **43 ocorrências residuais** (20 músicas), todas
`Emp` sobre dominantes-7 com `degree=?` — o "bV7→Emp genérico, ambíguo honesto" que
sobrou depois da adjudicação de `TRITONE-ADJUDICATION.md` (532→…→43). Hoje esse resíduo
é só uma view: o overlay ML **rankeia** a suspeita (surpresa), mas o veredito do Chediak
nunca **volta ao sistema de forma estruturada** — a malha neuro-simbólica fica aberta. A
sonda de geometria (centro + resolução) mostra que o resíduo NÃO é homogêneo: há assinatura
de SubV (`#11` natural: `samba-de-uma-nota-so` Ab7#11×6, `aqui-o` Bb7#11, `beatriz` A7#11,
`ausencia-de-voce` B7#11), aproximação cromática descendente (`minha-namorada` Eb7→E7,
`eh-menina` Ab7→A7) e empréstimo modal genuíno (`bye-bye-brasil` Bb7→Em7). Adjudicar esses
43 pela GEOMETRIA (raiz vs. tônica + resolução, não pelo rótulo) contra Chediak Vol. I —
que já está em `base_estudo/` — converte o resíduo em **fatos musicológicos citados** e
fecha a malha: o ML ordena o que olhar, o Chediak decide, o resultado vira artefato.

## What Changes

- **Novo corpus tipado de adjudicação** (`harmonic_analysis.corpus.tritone_adjudications`,
  molde de `corpus.modal_centers`): cada ocorrência do ledger recebe um `TritoneVerdict`
  com **citação Chediak obrigatória** (`Citation` com `__post_init__` — sem página o fato
  não existe; teste-invariante = gate) e um `verdict` de enum fechado
  (`subv` · `chromatic_approach` · `emp_legitimate` · `dsec_deceptive` · `ambiguous`).
- **Camada de ANOTAÇÃO (PRATA), não mutação.** O corpus **nunca** reescreve `function_code`
  do coder. Se um veredito confirmar defeito real (ex.: `Ab7(#11)` deveria ser SubV, não
  `Emp`), isso vira **change de fix downstream separada** — precedente exato:
  `TRITONE-ADJUDICATION.md` gerou `fix-tritone-t-by-degree` e `classify-special-function-dominants`.
- **Cruzamento no ledger + report.** `v_ledger_tritone_nondominant` passa a expor o
  `verdict` + a página citada por ocorrência; `harmonic corpus report` mostra a contagem
  por veredito (denominador visível, **nunca placar**).
- **Anti-drift.** `scripts/audit_tritone_adjudication.py` (molde do `audit_completeness.py`):
  re-deriva as ocorrências do ledger com a extração corrente e **falha** se alguma não
  estiver adjudicada OU marcada `ambiguous` explicitamente — o resíduo honesto é declarado,
  nunca silencioso.
- **Adjudicação página-a-página** das 43 (geometria + citação), com o resíduo genuinamente
  indecidível marcado `ambiguous` (com nota do porquê), não forçado.

## Capabilities

### New Capabilities
- `tritone-adjudication`: corpus tipado de vereditos citados para o ledger de trítono
  (identidade por música+posição), com citação obrigatória como gate, enum de veredito,
  lookup, cruzamento no report e auditoria anti-drift. Camada de anotação PRATA — não toca
  o coder.

### Modified Capabilities
- `corpus-query-gates`: a view `v_ledger_tritone_nondominant` SHALL expor o veredito
  adjudicado + a citação por ocorrência (aditivo; o ledger segue informativo, não bloqueia).

## Impact

- **Código novo:** `packages/harmonic_analysis/src/harmonic_analysis/corpus/tritone_adjudications.py`
  (+ export no `corpus/__init__.py`); enriquecimento de `persistence/views.sql`
  (`v_ledger_tritone_nondominant`) e `persistence/report.py` / seção do `corpus report`;
  `scripts/audit_tritone_adjudication.py`.
- **Dados:** o corpus é fato-em-código (como `modal_centers`), sem migração de schema
  obrigatória; o cruzamento na view é aditivo (rollback = reverter a view). Fronteira de
  copyright: só FATOS (veredito/página/nota/geometria), nunca texto/tabela/cifra do livro.
- **Invariantes:** os 3 gates duros seguem **293/293**; `function_code`/`degree` do coder
  **intocados** (invariante PRATA, testado). Nenhuma métrica de acurácia contra o coder.
- **Fora de escopo (downstream):** qualquer *fix* do coder motivado por um veredito
  (reclassificar SubV/cromático) é change separada.
