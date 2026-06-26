# Tasks — capture-song-key

## 1. Extrair o tom
- [x] 1.1 `_extract_tom(soup)` no scraper; `key` no dict de `scrape_cifra`.

## 2. Propagar
- [x] 2.1 Campo `key` no modelo `Cifra` (from_api/to_dict).
- [x] 2.2 Repositório repassa `raw_data["key"]` ao `Cifra`.

## 3. Verificação
- [x] 3.1 `_extract_tom` extrai "G"/"Am" de HTML representativo; "" quando ausente.
- [x] 3.2 `Cifra` round-trip preserva `key`.
- [x] 3.3 Suíte completa verde.
