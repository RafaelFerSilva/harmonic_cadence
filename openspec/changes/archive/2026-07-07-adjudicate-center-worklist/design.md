## Context

A worklist de centro tem 46 divergências (`center_status='diverge'`, n=293). O
`scripts/worklist_adjudication.py` (READ-ONLY) já as clusteriza pela relação harmônica
det→funcional: `paralela` (12), `2ªM` (10), `outra` (9), `IV↔I` (7), `V↔I` (5), `relativa` (3).
A `WORKLIST-ADJUDICATION.md` (n=170, 2026-07-01) já adjudicou 32 casos contra Chediak pp.84-85/87
(tônica repousa, V é tensão), com o achado central: **não há vencedor único** — funcional-certo
(14), detect-certo (9), armadilha ii-V (3), modulantes (6).

Cruzando a worklist corrente com a adjudicação prévia, ~24 dos 46 têm veredito citável com
geometria idêntica (ex.: `eh-menina`→detect Ré maior; `ciume`/`poema-azul`/`inutil-paisagem`→
functional; `bolinha-de-sabao`/`menina`/`rio`→armadilha ii-V com o I em Dó/Dó/Fá). O restante é
novo em n=293 (ex.: `desafinado`, `e-luxo-so`, `menino-das-laranjas`, `bloco-do-eu-sozinho`) ou
teve o centro funcional deslocado pela evolução do motor (`razao-de-viver` funcional D→C) e pede
reexame pela cadência visível.

O precedente de arquitetura é `adjudicate-tritone-ledger` (corpus tipado + citação-gate + tabela
derivada + view + anti-drift + report), que esta change espelha 1:1 no domínio do centro.

## Goals / Non-Goals

**Goals:**
- Converter as 46 divergências em vereditos citados (centro adjudicado + `winner` + evidência +
  Chediak pp.84-85/87), com modulante/indecidível marcado explícito.
- Materializar como corpus tipado (`corpus.tonal_center_adjudications`), citação = gate.
- View `v_center_worklist` + distribuição no report; anti-drift cobrindo toda a worklist.

**Non-Goals:**
- **NÃO** tocar `detect_key`/`chediak_functional_center`/`center_status` (invariante PRATA). Um
  gate cirúrgico do detector motivado por um veredito (armadilha ii-V; V-como-tônica) = change de
  **fix downstream** (precedente: `add-cadential-v-as-tonic-path`).
- **NÃO** medir acurácia contra nenhum método (a análise funcional é invariante a transposição; a
  tonalidade absoluta é só quadro de exibição).
- **NÃO** confundir com `modal-center-arbitration` (centro MODAL grego não-codificado); aqui é a
  divergência do centro TONAL entre dois métodos do motor.

## Decisions

**1. Corpus tipado espelhando `tritone_adjudications`.**
`TonalCenterVerdict` frozen dataclass: `slug`, `curated_root` (str, ex. "D"), `curated_mode`
(`Literal["major","minor"]`), `winner` (enum fechado), `evidence` (str, a cadência visível),
`citation` (opcional só p/ `ambiguous`). Reusa a `Citation` de `modal_centers` (gate por
importação). Identidade = `slug` (uma divergência por música — center é por-música, ≠ trítono que
é por-ocorrência). *Alternativa descartada:* tabela DuckDB solta — perde o gate-por-importação e a
fronteira de copyright em código.

**2. Enum de `winner` que codifica o achado do #7.**
`detect` · `functional` · `neither_ii_v` · `modulating` · `ambiguous`. O `neither_ii_v` é 1ª
classe porque a armadilha do ii-V é o achado mais instrutivo (a tônica é o ALVO do V, sub-
representada). *Alternativa descartada:* binário detect/functional — apagaria a armadilha e os
modulantes, forçando um vencedor falso (viola "nunca chute").

**3. Centro adjudicado guardado explícito (raiz+modo), não só o vencedor.**
Molde do `modal_centers` (guarda o centro curado). Para `detect`/`functional` o centro adjudicado
= o do método vencedor; para `neither_ii_v` é o I (terceiro valor, ex. Dó em `bolinha-de-sabao`);
para `modulating`/`ambiguous` é o melhor palpite do fim/região com nota de baixa confiança. Isso
torna o fato auto-contido e auditável.

**4. Cruzamento via tabela derivada + view nova (aditivo).**
No `corpus build`, materializa `center_adjudication` (do corpus-em-código, chave slug→song_id) e
cria `v_center_worklist` (LEFT JOIN às músicas `diverge`). Molde exato do `tritone_adjudication`.
Rollback = DROP + reverter a view.

**5. Citação de MÉTODO, não por-música-inventada.**
A citação é Chediak pp.84-85/87 (o critério funcional: tônica=repouso, V=tensão) — a regra sendo
aplicada às cadências visíveis, não uma página fabricada por canção. É o mesmo padrão honesto da
`WORKLIST-ADJUDICATION.md`. A evidência (o par cadencial visível) é o "porquê" específico.

## Risks / Trade-offs

- **[Veredito prévio não transfere — centro funcional deslocou entre runs]** → reexame obrigatório
  quando o valor corrente diverge do adjudicado em 2026-07-01 (`razao-de-viver`); não copiar cego.
- **[Tentação de gatear o detector aqui]** → Non-Goal explícito; fix é downstream. Mantém gates
  293/293 triviais (nada no motor muda).
- **[Modulantes/relativa-ambígua sem centro único]** → `modulating`/`ambiguous` com nota; não
  força vencedor (o achado do #7 legitima o resíduo).
- **[Confusão com `modal_centers`]** → nomes e docstrings distinguem; escopos disjuntos (modal
  grego vs. tonal detect×funcional).

## Migration Plan

1. Corpus-em-código + testes de invariância (citação/enum/lookup) — sem tocar o build.
2. Adjudicar as 46 (reusa prévias onde bate; reexame do resto) até a auditoria zerar.
3. Tabela derivada + `v_center_worklist` + seção no report (aditivo).
4. `songbook_baseline.py` + `corpus gates`: 3 gates duros 293/293, centro 216/262 intacto.
Rollback: reverter view/tabela (o corpus-em-código é inerte sem o cruzamento).

## Open Questions

- Os `paralela` (12, mesma raiz, modo trocado) são a maior classe: o "vencedor" é sobre o MODO,
  não a região. Decidir por música se a evidência (repouso maior vs. menor) fecha o modo ou fica
  `ambiguous` — resolve-se na adjudicação, caso a caso.
- Se `neither_ii_v` ou `V↔I` formarem uma classe grande e limpa, a change de fix downstream do
  `detect_key` pode valer priorização — decisão pós-adjudicação, fora deste escopo.
