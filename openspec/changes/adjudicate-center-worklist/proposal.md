## Why

A corroboração de centro (`detect_key` × `chediak_functional_center`) tem **46 divergências**
(`v_song_current.center_status = 'diverge'`, n=293). Hoje elas são só uma contagem
(`v_center_ledger`) + um Markdown de adjudicação prévio (`WORKLIST-ADJUDICATION.md`, n=170, 32
casos) que **não volta ao sistema estruturado** — a malha fica aberta, como estava o trítono. O
achado do #7 é rochoso: **não há regra-cega segura** — cada método falha de um jeito
(funcional-certo quando o K-S agarra V/IV/ii/iii/relativa; detect-certo quando o achador funcional
agarra um v/ii/pivô tonicizado; a **armadilha do ii-V** onde nenhum pega a tônica; e modulantes sem
centro único). Adjudicar os 46 pela GEOMETRIA (cadência visível: tônica repousa, V é tensão,
Chediak pp.84-85/87) — **nunca** pela anotação do CC — converte a worklist em **fatos citados** e
fecha a malha, exatamente como `adjudicate-tritone-ledger` fez com o trítono. É pré-requisito para
qualquer gate cirúrgico futuro do `detect_key` (saber, com citação, quais casos o detector erra).

## What Changes

- **Novo corpus tipado** (`harmonic_analysis.corpus.tonal_center_adjudications`, molde de
  `tritone_adjudications`/`modal_centers`): cada música-divergência recebe um
  `TonalCenterVerdict` com o **centro adjudicado** (raiz + modo), um `winner` de enum fechado
  (`detect` · `functional` · `neither_ii_v` · `modulating` · `ambiguous`), a **evidência** (a
  cadência visível que decide) e **citação Chediak obrigatória** (pp.84-85/87 — o critério
  funcional; sem citação o fato não existe, exceto `ambiguous`).
- **Camada de ANOTAÇÃO (PRATA), não mutação.** O corpus **nunca** toca `detect_key`,
  `chediak_functional_center`, `center_pc`/`center_status` nem os 3 gates duros. Se um veredito
  revelar uma classe que o `detect_key` erra de forma cirurgicamente corrigível (ex.: a armadilha
  ii-V, ou V-como-tônica alta-confiança), isso vira **change de fix downstream separada** —
  precedente: `add-cadential-v-as-tonic-path` (Path C) e a própria `adjudicate-tritone-ledger`.
- **Worklist como view + cruzamento.** Nova view aditiva `v_center_worklist` (as músicas
  `diverge` + detect/funcional + o veredito adjudicado + página) e a distribuição por veredito no
  `harmonic corpus report` (denominador visível, **nunca placar** — a divergência não penaliza
  método algum; a análise funcional é invariante a transposição).
- **Anti-drift.** `scripts/audit_center_adjudication.py` (molde `audit_tritone_adjudication`):
  re-deriva as músicas `diverge` da extração corrente e **falha** se alguma ficar sem veredito ou
  houver veredito órfão.
- **Adjudicação das 46** (reusa `WORKLIST-ADJUDICATION.md` onde a geometria corrente bate; reexame
  dos casos novos/deslocados como `razao-de-viver` funcional D→C), com o modulante/indecidível
  marcado explícito.

## Capabilities

### New Capabilities
- `tonal-center-adjudication`: corpus tipado de vereditos citados para a worklist de centro
  (identidade por música), com centro adjudicado + `winner` + evidência + citação obrigatória
  como gate, lookup, view `v_center_worklist`, cruzamento no report e auditoria anti-drift.
  Camada de anotação PRATA — não toca o detector nem o achador funcional. Distinto de
  `modal-center-arbitration` (aquele anota CENTRO MODAL grego que a cifra não codifica; este
  adjudica a divergência do centro TONAL entre dois métodos do próprio motor).

### Modified Capabilities
<!-- Nenhuma: a worklist de centro vira view nova; o detector e o achador funcional ficam intactos. -->

## Impact

- **Código novo:** `packages/harmonic_analysis/src/harmonic_analysis/corpus/tonal_center_adjudications.py`
  (+ export no `corpus/__init__.py`); nova view em `persistence/views.sql` (`v_center_worklist`,
  aditiva) materializada da tabela derivada `center_adjudication` (schema aditivo, molde de
  `tritone_adjudication`); seção no `persistence/report.py`; `scripts/audit_center_adjudication.py`.
- **Dados:** fato-em-código (como `modal_centers`); a tabela derivada e a view são aditivas
  (rollback = DROP + reverter a view). Fronteira de copyright: só FATOS (centro/veredito/evidência/
  página), nunca cifra/tabela do livro; a evidência descreve a cadência da PRÓPRIA música.
- **Invariantes:** 3 gates duros seguem **293/293**; `detect_key`/`center_status` **intocados**
  (PRATA testado). Nenhuma métrica de acurácia — a worklist é curadoria, não placar.
- **Fora de escopo (downstream):** qualquer gate/fix do `detect_key` motivado por um veredito.
