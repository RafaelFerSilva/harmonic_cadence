## Why

O retrieval de similaridade (`harmonic-similarity-retrieval`) responde "1-para-1" — vizinhos de UMA
música. Falta o **mapa do corpus inteiro**: quais **famílias harmônicas** existem entre as 293
músicas, e qual é a **música-protótipo** (mais central) de cada família. Isso transforma a matriz de
similaridade que já materializei num retrato musicológico do songbook ("há N dialetos harmônicos na
bossa deste corpus; o centro de cada um é tal música"), e cada outlier de família vira candidato à
curadoria (insumo da Trilha A). É a próxima capability descritiva da Camada C — reusa tudo o que já
existe, sem dependência nova.

## What Changes

- **Agrupamento hierárquico** (aglomerativo, *average-linkage*) sobre a distância de cosseno entre os
  embeddings harmônicos por música — **puro Python, sem dependência ML** (293 músicas é trivial),
  reusando os vetores de `style_fingerprint` num eixo de funções **global** (comparabilidade). O
  usuário escolhe o número de famílias `--k` (padrão 8); **nenhuma alegação de "k ótimo"** (é
  descritivo, não placar).
- **Música-protótipo (medoid)** por família: a de maior similaridade média com as demais da família.
- **Materialização** `song_cluster` (`run_id`, `song_id`, `cluster_id`, `is_medoid`) + view
  `v_song_cluster` (com títulos), derivada/regenerável, aditiva.
- **CLI `harmonic corpus clusters [--k N]`:** por família, tamanho, protótipo, membros e os **traços
  harmônicos salientes** que a definem (funções/cadências dominantes) — o "porquê" da família visível.
- Descritivo: **não** reescreve coder, **não** arbitra, **não** toca gates. Família ≠ qualidade.

## Capabilities

### New Capabilities
- `harmonic-corpus-clustering`: agrupamento hierárquico das músicas por perfil harmônico (reusando o
  embedding/similaridade de estilo), identificação do medoid por família, materialização
  `song_cluster`/`v_song_cluster`, e o subcomando `corpus clusters` com os traços que definem cada
  família. Descritivo, transposição-invariante, nunca arbitra.

### Modified Capabilities
<!-- Nenhuma. Reusa `harmonic-similarity-retrieval`/`style-fingerprint` sem alterar seus requisitos. -->

## Impact

- **Código:** novo `overlay/clustering.py` (aglomerativo puro-Python + medoid + materialização);
  reusa `overlay/similarity.fingerprint_from_db` e `style_fingerprint`; ação `clusters` + flag `--k`
  no `corpus` da CLI; testes.
- **Banco:** tabela `song_cluster` + view `v_song_cluster` (aditivo/derivado; rollback = DROP).
- **Não toca:** os 3 gates duros (293/293), `detect_key`, `function_code`/`degree`, a persistência
  base, nem os requisitos das capabilities reusadas. Mede contra `songbook_baseline.py` ao vivo.
- **Sem dependência nova:** stdlib apenas (o cosseno e os fingerprints já existem).
