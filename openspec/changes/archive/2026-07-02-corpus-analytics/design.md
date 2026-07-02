## Context

O banco DuckDB (`persist-analysis-corpus`) já disseca as 170 análises: fato
`chord_occurrence` (grão = acorde numa posição, ~8.500 linhas), cabeçalho `song`
(centro/ledger), satélites `cadence` (com posição reconstruída), `chord_vocab` (parse único,
`category`/`has_real_tritone`), dimensões `function_ref`/`cadence_family_ref` (com página
Chediak). Views existentes: 3 gates executáveis, `v_ledger_tritone_nondominant` (pós-isenção
I7), `v_center_ledger`, `v_function_bigram`. Esta change só LÊ esse estado.

Restrições herdadas: banco nunca é ouro (relatório descreve, não pontua); degradação visível;
relatórios humanos em PT-BR; Chediak citado onde a dimensão já carrega a página.

## Goals / Non-Goals

**Goals:**
- Views de analytics: cadências por família, trigramas de função, vocabulário por modo,
  densidade de secundários por música, ledger de trítono agrupado por padrão.
- `harmonic corpus report` → Markdown descritivo em PT-BR consolidando as views.
- A seção do ledger agrupada por padrão vira insumo da adjudicação (frente A).

**Non-Goals:**
- Nenhum ML/estatística inferencial (é a Change C do roadmap exploratório).
- Nenhuma mudança no motor, no schema das tabelas ou nos gates.
- Sem HTML no MVP (o projeto tem `presentation/reports/html.py` para análise de MÚSICA, não de
  corpus; o relatório de corpus nasce Markdown — HTML só se houver demanda).

## Decisions

### D1 — Tudo é view SQL; o Python só formata
As agregações vivem em `views.sql` (declarativas, auditáveis, testáveis por SQL direto);
`report.py` apenas consulta e renderiza Markdown. *Alternativa:* agregar em pandas/Polars —
rejeitado (dependência nova sem necessidade; DuckDB agrega melhor).

### D2 — Trigrama via dupla auto-junção por posição
`v_function_trigram`: junta `chord_occurrence` consigo em `position+1` e `position+2`
(mesmo `song_id`). N-grams maiores ficam fora do MVP (o retorno cai e a view explode em
cardinalidade); bigrama já existe.

### D3 — Ledger agrupado por padrão = `function_code × degree_base × quality`
`v_tritone_ledger_patterns`: agrupa o ledger por (função-alvo, grau-base normalizado, qualidade
do vocab), com contagem, nº de músicas e até 3 símbolos-exemplo (`ANY_VALUE`/`MIN` — DuckDB tem
`arg_min`; usar `MIN(symbol)` + `COUNT(DISTINCT song_id)` para portabilidade). Normalização do
grau-base (tira `°`/`m`/inversão) é feita com `regexp_replace` no SQL — espelha `degree_base`
do motor para os casos presentes (graus romanos com sufixos), documentado no teste.

### D4 — Densidade de secundários por macro-categoria da dimensão
`v_secondary_density`: % de ocorrências com `function_ref.macro_category='D'` E
`function_code != 'D'` (dominante NÃO-primário: `Dsec/Daux/Dext/SubV/Sub2/D2/Dim`… — usar a
lista explícita `('Dsec','Daux','Dext','SubV','Sub2')` para ficar fiel ao conceito de
"secundário/substituto") sobre `n_chords`, por música, com média do corpus.

### D5 — Relatório em `persistence/report.py`, saída `corpus-report.md`
Função `render_report(conn) -> str` (pura, testável) + gravação pelo handler CLI (`--out`
configurável). Seções fixas: 1 Corpus (runs, músicas, ledger de centro), 2 Cadências,
3 Progressões (bigrama/trigrama top-N), 4 Vocabulário por modo, 5 Dominantes
secundários, 6 Ledger de curadoria (padrões). Números sempre com denominador visível
(nunca % solto). PT-BR.

### D6 — `corpus report` reusa o subcomando existente
`action` do parser ganha a choice `report` (+ `--out`, default `corpus-report.md`). Mesmo
padrão de import tardio e de falha visível com banco vazio.

## Risks / Trade-offs

- **[View de trigrama cara]** → corpus é minúsculo (~8.5k linhas); irrelevante. Se o corpus
  crescer 100×, materializar então.
- **[Relatório lido como placar]** → linguagem do template é descritiva ("distribuição",
  "ocorrências"), seção 6 nomeada "worklist de curadoria"; nenhum "acerto/erro".
- **[`degree` cru no agrupamento]** → graus vêm do motor com sufixos (`II°`, `v`); a
  normalização SQL pode divergir de `degree_base` em caso exótico → teste de paridade da
  normalização sobre os graus distintos presentes no banco.

## Migration Plan

Aditivo. Rollback = remover views novas, `report.py` e a choice `report`. Bancos existentes
ganham as views no próximo `init_db` (CREATE OR REPLACE).

## Open Questions

- Top-N das listas do relatório (proposta: 15 para progressões, 10 para padrões do ledger,
  configurável depois se doer).
