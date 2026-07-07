## Why

O corpus tem 293 músicas dissecadas no DuckDB (grão de ocorrência), mas não há como perguntar
"**quais músicas são harmonicamente parecidas com esta?**". A resposta é MIR clássico e puramente
descritivo — e, crucialmente, pode ser **transposição-invariante** (comparar por FUNÇÃO, não por
tom), o que casa com o princípio central do projeto. O projeto já tem a maquinaria de comparação
(`domain/style_fingerprint`: distribuição de função, matriz de transição, cosseno, Jensen-Shannon),
mas só em **grão de artista, em memória**. Falta o grão de **música**, alimentado pelo corpus
persistido, com uma camada de **retrieval de vizinhos**. É a próxima capability descritiva da
Camada C (não arbitra nada; similaridade ≠ qualidade).

## What Changes

- **Embedding harmônico por música:** um `Fingerprint` (reusando o dataclass de `style_fingerprint`)
  construído do DuckDB para CADA música — distribuição de função, matriz de transição função→função,
  contagem de cadências, uso modal, densidade de tensão. Transposição-invariante (funções são
  relativas), interpretável ("bag-of-progressions"), sem ML pesado.
- **Similaridade + vizinhos:** similaridade de cosseno (reusando `style_fingerprint.similarity`)
  entre todos os pares; materializa os **top-K vizinhos** por música numa tabela `song_neighbor`
  (derivada/regenerável) + view `v_song_neighbor` com títulos.
- **CLI `harmonic corpus similar --song <slug> [--k N]`:** lista as músicas mais próximas com a
  similaridade e os **traços compartilhados** (funções/cadências salientes em comum) — o "porquê"
  visível, não um número solto.
- Descritivo: **não** reescreve nada do coder, **não** arbitra centro, **não** toca gates —
  similaridade não é veredito de qualidade.

## Capabilities

### New Capabilities
- `harmonic-similarity-retrieval`: embedding harmônico por música (do corpus persistido, reusando o
  fingerprint de estilo), similaridade de cosseno, materialização dos top-K vizinhos, e o subcomando
  `corpus similar` com explicação dos traços compartilhados.

### Modified Capabilities
<!-- Nenhuma. `style-fingerprint` (grão de artista, em memória) é REUSADO, não alterado —
     nenhum requisito seu muda. -->

## Impact

- **Código:** novo `overlay/similarity.py` (fingerprint por música do DuckDB + build de vizinhos);
  reusa `domain/style_fingerprint` (`Fingerprint`, `similarity`, `jensen_shannon`); flags `--song`
  e `--k` + ação `similar` no `corpus` da CLI; testes.
- **Banco:** tabela `song_neighbor` + view `v_song_neighbor` (aditivo/derivado; rollback = DROP).
- **Não toca:** os 3 gates duros (293/293), `detect_key`, `function_code`/`degree`, a persistência
  base, nem os requisitos de `style-fingerprint`. Mede contra `songbook_baseline.py` ao vivo.
- **Sem dependência nova:** stdlib + o cosseno já existente (nada de numpy/sklearn nesta change).
