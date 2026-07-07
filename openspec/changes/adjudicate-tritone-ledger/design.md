## Context

O ledger `v_ledger_tritone_nondominant` tem 43 ocorrências residuais (20 músicas), todas
`Emp` sobre dominantes-7 com `degree=?`. É o resíduo pós-adjudicação (532→…→43): trítono real
que o coder leu como empréstimo modal, mas cuja geometria (raiz vs. centro + resolução) não foi
verificada caso a caso. A sonda ao vivo (join `chord_occurrence` × acorde seguinte) mostra três
regimes distintos misturados sob o mesmo rótulo `Emp`:

- **Assinatura SubV** (`#11` natural): `samba-de-uma-nota-so` Ab7(#11)×6, `aqui-o` Bb7(#11),
  `beatriz` A7(#11), `ausencia-de-voce` B7(#11) → `F7M` (repouso).
- **Aproximação cromática descendente** (resolve num dominante um semitom acima):
  `minha-namorada` Eb7→E7, `eh-menina` Ab7→A7(9), `demais` Eb7→E7(b9).
- **Empréstimo modal genuíno** (bVI7/bVII7 → repouso): `bye-bye-brasil` Bb7→Em7,
  `o-amor-e-chama` Bb7→Em7(9), `garota-de-ipanema` B7→F#m7 (deceptivo).

O precedente de método é `TRITONE-ADJUDICATION.md` (Chediak XXXIV pp.111-116): adjudicar pela
GEOMETRIA, não pelo rótulo; e o precedente de arquitetura é `corpus.modal_centers` (fato-em-
código, citação obrigatória com `__post_init__` como gate, transposição-seguro, lookup por
identidade slug). Esta change combina os dois: a adjudicação vira um corpus tipado igual ao
`modal_centers`, e o veredito volta cruzado no ledger/report.

## Goals / Non-Goals

**Goals:**
- Converter as 43 ocorrências em vereditos citados (Chediak Vol. I, `base_estudo/`), com o
  resíduo indecidível marcado `ambiguous` explícito (nota do porquê).
- Materializar os vereditos como corpus tipado (`corpus.tritone_adjudications`), citação = gate.
- Fechar a malha: veredito + página cruzados em `v_ledger_tritone_nondominant` e no `corpus report`.
- Auditoria anti-drift (`audit_tritone_adjudication.py`) que garante cobertura total do ledger.

**Non-Goals:**
- **NÃO** reescrever `function_code`/`degree` do coder (invariante PRATA). Um veredito que
  confirme defeito real (SubV/cromático mal-rotulado como `Emp`) motiva uma change de **fix
  downstream separada** — precedente: a adjudicação de 2026-07-02 gerou `fix-tritone-t-by-degree`
  e `classify-special-function-dominants`.
- **NÃO** medir acurácia contra o coder (discordância = sinal, não erro).
- **NÃO** crescer o corpus de músicas (congelado em n=293).

## Decisions

**1. Corpus tipado espelhando `modal_centers` (não tabela solta / não JSON).**
`TritoneVerdict` frozen dataclass com `Citation` obrigatória (reusa o padrão `__post_init__`
falha-rápido). Identidade = `slug|position` (a mesma chave do ledger), não `(artista, música)`
como `modal_centers`, porque há múltiplas ocorrências por música (e.g. `samba-de-uma-nota-so`
tem 6). *Alternativa descartada:* armazenar em tabela DuckDB — perderia o gate-por-importação e
a fronteira de copyright explícita em código; o fato-em-código é auditável em review e versionado.

**2. Enum fechado de veredito geométrico.**
`subv` · `chromatic_approach` · `emp_legitimate` · `dsec_deceptive` · `ambiguous`. Fechado para
forçar a disciplina "cada caso cai numa categoria citável OU é ambíguo declarado". *Alternativa
descartada:* texto livre — reintroduz o rótulo-ingênuo que a regra de ouro proíbe.

**3. Cruzamento na view via LEFT JOIN a uma tabela derivada do corpus.**
No `corpus build`, materializa uma tabela `tritone_adjudication` (derivada do corpus-em-código,
regenerável) e a view faz LEFT JOIN por `(song_id via slug, position)`. Ocorrência não-adjudicada
→ veredito NULL (não some da view). Aditivo: rollback = reverter a view + DROP da tabela.
*Alternativa descartada:* JOIN direto contra o módulo Python na consulta — SQL não chama Python;
a materialização derivada no build é o padrão já usado por `song_cluster`/`song_neighbor`.

**4. Anti-drift no molde `audit_completeness.py`.**
Re-deriva o ledger com a extração corrente e faz diff simétrico contra as chaves do corpus:
ocorrência sem veredito → falha; veredito órfão → falha. Roda no CI/manual, não no build.

**5. Adjudicação é trabalho de conhecimento, feita na implementação.**
Cada uma das 43 é resolvida lendo a geometria (já extraída na sonda) + a página do Chediak em
`base_estudo/` (página do PDF = página do livro). Os padrões já mapeados (SubV por `#11`,
cromático descendente, empréstimo genuíno) guiam, mas cada veredito cita a página específica;
o que não fechar vira `ambiguous` com nota — nunca chute.

## Risks / Trade-offs

- **[Adjudicação errada / citação imprecisa]** → cada veredito cita página verificável em
  `base_estudo/`; casos duvidosos → `ambiguous`, não força. Review humano do curador (o próprio
  usuário, autoridade Chediak) é o gate final.
- **[Veredito revela defeito do coder e há tentação de "consertar aqui"]** → Non-Goal explícito:
  fix é change downstream. Esta change só registra o fato citado; mantém o invariante PRATA
  testado (função/grau intocados).
- **[Drift silencioso ao mudar a extração]** → auditoria anti-drift falha-rápido cobre exatamente
  isso; é o mesmo padrão que pegou drift zero em completude.
- **[Chave slug|position frágil a re-materialização]** → a posição é estável dado o corpus
  congelado (n=293, extração determinística); a auditoria detecta qualquer desalinhamento.

## Migration Plan

1. Corpus-em-código + testes de invariância (citação/enum/lookup) — sem tocar o build ainda.
2. Adjudicar as 43 (preenche o corpus) com a auditoria acusando as pendentes até zerar.
3. Materialização derivada + LEFT JOIN na view + seção no report (aditivo).
4. Rodar `songbook_baseline.py` e `corpus gates`: confirmar 3 gates duros 293/293 e coder intocado.
Rollback: reverter a view/tabela derivada (o corpus-em-código é inerte sem o cruzamento).

## Open Questions

- Alguns casos (e.g. `flora` com `center=None`, `samba-de-uma-nota-so`/`aqui-o` com centro
  instável) podem não ter centro tonal confiável para fixar o grau — provável cluster de
  `ambiguous` honesto. Resolve-se na adjudicação, caso a caso.
- Se o volume de `subv`/`chromatic_approach` confirmados for alto, a change de fix downstream
  pode valer priorização imediata — decisão pós-adjudicação, fora deste escopo.
