## Why

O Cifra Club mostra o **tom** da música na própria página (elemento `#cifra_tom`),
**na mesma fonte dos acordes** — ou seja, é uma anotação de tonalidade *alinhada
ao dado* (sem o risco de transposição de uma fonte externa). Hoje o scraper
**encontra esse elemento e o descarta** (`cifra_tom_elem.decompose()`, ao limpar
o HTML) — joga fora um dado útil.

Capturá-lo destrava a **Fase A** (corpus de validação): toda música scrapada
passa a carregar seu tom de referência, contra o qual medir a acurácia da
detecção de tonalidade.

## What Changes

- O scraper **extrai o tom** do `#cifra_tom` (antes de descartá-lo) e o inclui no
  resultado.
- O modelo `Cifra` ganha o campo **`key`** (o tom da fonte; `""` quando ausente).
- O repositório repassa o `key` do scraper ao `Cifra`.

Fora de escopo: o harness de acurácia e a comparação detectado-vs-anotado (próxima
change); normalizar/validar o tom (é "prata" — crowd-sourced, pode ter ruído).

## Capabilities

### Modified Capabilities
- `cifra-core`: o contrato `Cifra` passa a carregar o tom da música quando a
  fonte o informa.

## Impact

- `cifra_scraper/.../cifraclub_scraper.py`: `_extract_tom` + `key` no dict.
- `cifra_core/models.py`: campo `key` no `Cifra` (from_api/to_dict).
- `cifra_scraper/.../repositories/cifraclub.py`: repassa `key`.
- O `key` da fonte (anotação) é distinto do `key` *detectado* na análise — vivem
  em objetos diferentes (entrada vs resultado).
- Testes: extração do tom de um HTML representativo; round-trip do `Cifra`.
