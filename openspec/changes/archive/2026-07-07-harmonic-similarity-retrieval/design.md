## Context

O DuckDB (run 5, n=293) tem tudo para um fingerprint por música: `chord_occurrence` (função/grau
por posição), `cadence` (família por música), `modal_coloring` (453 linhas), `function_ref`
(`is_repose` → tensão). O `domain/style_fingerprint` já implementa o `Fingerprint` (distribuição de
função + matriz de transição + cadências + modal + tensão), o vetor achatado (`_feature_vector`,
transposição-invariante por ser sobre funções), e `similarity`/`jensen_shannon` — tudo testado.
Falta o **grão de música** (o fingerprint atual é de artista, em memória sobre `result` dicts) e a
**camada de retrieval**.

## Goals / Non-Goals

**Goals:**
- Responder "quais músicas são harmonicamente próximas de X" com um embedding **interpretável e
  transposição-invariante**, reusando a matemática já testada.
- Materializar top-K vizinhos (derivado/regenerável) + CLI com o "porquê" (traços compartilhados).
- Zero regressão; descritivo (não arbitra, similaridade ≠ qualidade).

**Non-Goals:**
- NÃO embeddings aprendidos (song2vec/autoencoder) nesta change — o count-based é honesto e sem
  dependência; aprendido é follow-up.
- NÃO clustering/visualização nesta change (a tabela de vizinhos habilita isso depois).
- NÃO duplicar a matemática de cosseno — reusar `style_fingerprint`.

## Decisions

**D1 — reusar `style_fingerprint.Fingerprint` + `similarity`, construindo por música do DB.** Novo
`fingerprint_from_db(conn, song_id) -> Fingerprint` monta o MESMO dataclass a partir de agregados
do DuckDB (`song_count=1`), e a comparação reusa `similarity`/`jensen_shannon` sem reescrita.
*Alternativa:* re-rodar o motor por música para obter `result` dicts e chamar `build_fingerprint` —
rejeitado: o `corpus build` já rodou o motor; reprocessar é desperdício e acopla à rede/parse.

**D2 — embedding = vetor de estilo concatenado (função + transição + modal + tensão), cosseno.**
É transposição-invariante (funções relativas — alinha com "análise funcional invariante a
transposição"), interpretável ("bag-of-progressions"), e sem dependência nova. *Alternativa:*
Jensen-Shannon como métrica primária — mantida como secundária exposta (já existe), mas o cosseno
sobre o vetor rico (inclui transições) captura a "gramática", não só a distribuição marginal.

**D3 — materializar top-K vizinhos, não a matriz cheia.** 293² pares é trivial de computar, mas
guardar só top-K (`song_neighbor`, K default 10) mantém a tabela enxuta e serve o caso de uso
(retrieval). Regenerável por run; `similar` reconstrói se o run mudou. *Alternativa:* on-the-fly
por consulta — simples, mas materializar habilita analytics (clusters, "música mais central")
depois e segue o padrão do corpus persistido.

**D4 — CLI explica o "porquê".** `corpus similar --song X` mostra, por vizinho, a similaridade + os
traços salientes compartilhados (top funções em comum na distribuição; famílias de cadência em
comum). O "denominador visível" da similaridade: não um número mágico. Slug→song_id resolvido no
run corrente; slug inexistente = erro visível.

## Risks / Trade-offs

- **[Similaridade lida como "qualidade/correção"]** → Mitigação: a spec e a saída declaram que é
  relação descritiva; sem placar; a doc reforça similaridade ≠ juízo.
- **[Vetor dominado por T/SD/D (funções frequentes) achata a discriminação]** → Mitigação: a matriz
  de transição (144 dims) e cadências trazem estrutura fina; se provar pouco discriminante, um
  follow-up pode ponderar (TF-IDF sobre funções) sem mudar o schema.
- **[Músicas curtas/parciais viram outliers de similaridade]** → Mitigação: `completeness` está no
  banco; a CLI pode marcar vizinhos de cifra parcial (como o report de trítono já faz). v1 apenas
  expõe; ponderar é follow-up.
- **[Regressão nos gates]** → Mitigação: baseline ao vivo antes/depois; a spec exige 293/293 e
  coder intocado (o overlay só LÊ).

## Migration Plan

1. Aditivo: `CREATE TABLE IF NOT EXISTS song_neighbor` + `CREATE OR REPLACE VIEW v_song_neighbor`.
   Rollback = DROP dos dois; o resto do banco é intocado.
2. Sem migração de schema base; sem dependência de runtime nova.
3. `corpus similar` (re)materializa os vizinhos do run corrente sob demanda se ausentes/desatualizados.

## Open Questions

- **K default e métrica exposta:** K=10 e cosseno como primária, JSD secundária no detalhe. Ajustável
  por `--k`; se a curadoria preferir JSD, expor `--metric` é follow-up trivial.
- **Ponderação por completude/tamanho:** deixada como follow-up — v1 expõe `completeness` do vizinho,
  não pondera.
