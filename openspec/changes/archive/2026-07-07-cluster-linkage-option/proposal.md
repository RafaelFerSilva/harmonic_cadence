## Why

O clustering usa *average-linkage*, que no dado real (`k=8`) produz um **núcleo gigante** (247/293)
+ satélites: em vez de particionar o corpo da bossa, ele destaca outliers. Isso é honesto, mas limita
o uso — o usuário quer também uma partição mais **equilibrada** que revele sub-dialetos dentro do
núcleo. *Complete-linkage* (distância entre famílias = MAIOR distância par-a-par) favorece famílias
compactas e de tamanho parecido — a alavanca clássica para esse problema. Oferecer a escolha
(`--linkage`) dá as duas lentes sem trocar nada mais.

## What Changes

- O agrupamento ganha um parâmetro **`linkage`** — `average` (padrão, comportamento atual) ou
  `complete` (distância = máximo par-a-par → partição mais equilibrada). Puro Python, sem dep nova
  (reusa a mesma matriz de similaridade).
- `harmonic corpus clusters` ganha `--linkage {average,complete}` e reporta qual foi usado.
- Determinístico; descritivo; não toca coder/gates.

## Capabilities

### New Capabilities
<!-- Nenhuma. -->

### Modified Capabilities
- `harmonic-corpus-clustering`: o requisito "Agrupamento hierárquico por perfil harmônico" passa a
  aceitar o critério de ligação (`average`/`complete`) como parâmetro do usuário.

## Impact

- **Código:** `overlay/clustering.py` (`_agglomerate` parametriza a função de ligação; `build_clusters`
  recebe `linkage`); flag `--linkage` na CLI; testes.
- **Banco:** nenhuma mudança de schema.
- **Não toca:** os 3 gates duros (293/293), `detect_key`, coder, persistência base. Mede contra
  `songbook_baseline.py` ao vivo.
- **Sem dependência nova.**
