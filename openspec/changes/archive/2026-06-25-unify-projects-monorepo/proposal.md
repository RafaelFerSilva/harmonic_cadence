## Why

`harmonic_cadence` (analisador harmônico, Poetry/CLI) e `cifraclub_scrap_api` (scraper REST em Flask) já são **duas metades de um mesmo sistema**: o scraper produz a cifra em JSON e o analisador a consome via `http://localhost:3000/api`. Hoje eles vivem em repositórios separados, com toolchains diferentes (Poetry vs. pip), uma dependência de rede "invisível" e código já duplicado entre si (`fix_encoding` byte-a-byte idêntico, filtragem de linhas de cifra feita duas vezes com regras divergentes, dois dialetos de regex de acorde). Unificar formaliza o sistema que já existe, elimina a duplicação e remove a fricção de "preciso subir 2 projetos para analisar uma música".

## What Changes

- Consolidar os dois repositórios em um **monorepo** com pacotes separados: `cifra_core` (compartilhado), `cifra_scraper` (API Flask) e `harmonic_analysis` (domínio musical + CLI + relatórios).
- Extrair um pacote núcleo `cifra_core` com a **fonte única de verdade** para: correção de encoding, limpeza/filtragem de linhas de cifra, regex de acorde, normalização de slug e os modelos `Cifra`/`SongRef`.
- Introduzir a porta `SongProvider` como interface entre análise e obtenção de cifra, com dois adaptadores: `HttpSongProvider` (fala com o serviço Flask) e `InProcessSongProvider` (raspa no mesmo processo, sem subir servidor), e um decorator de cache. **BREAKING** para o uso interno: o `AnalysisService` deixa de depender de `infra/cifra_api` diretamente e passa a depender da porta.
- Unificar a toolchain de empacotamento em **`uv` workspaces** (substituindo Poetry e pip) — um único `pyproject` raiz, um `uv.lock`, um `docker-compose`, comandos únicos de build/test/run.
- Permitir que a CLI analise músicas **sem precisar subir a API** (via `InProcessSongProvider`).
- Eliminar a dupla filtragem de linhas: a API passa a devolver linhas **já limpas** (contrato D3) e a filtragem ocorre em um só lugar — filtro idempotente no `cifra_core`.

Fora de escopo (não-objetivos): reescrever a teoria musical, corrigir a detecção de tonalidade, recuperar as suítes de teste quebradas — são melhorias válidas, mas independentes desta unificação.

## Capabilities

### New Capabilities
- `song-provider`: abstração (porta) pela qual o analisador obtém cifras e listas de músicas, com adaptador HTTP, adaptador in-process e cache, selecionável por configuração.
- `cifra-core`: biblioteca núcleo compartilhada — fonte única para correção de encoding, pré-processamento/filtragem de linhas de cifra, regex de acorde, normalização de slug e os modelos `Cifra`/`SongRef`, consumida tanto pelo scraper quanto pelo analisador.
- `monorepo-structure`: estrutura de repositório único, com pacotes separados, toolchain de empacotamento unificada e fluxos únicos de build, teste, execução e deploy.

### Modified Capabilities
<!-- Nenhuma: openspec/specs/ está vazio; todas as capacidades acima são novas. -->

## Impact

- **Repositórios**: `harmonic_cadence` e `cifraclub_scrap_api` passam a um monorepo; os históricos são preservados via `git subtree` (decisão tomada).
- **Código (analisador)**: `harmonic_cadence/infra/cifra_api.py` e `harmonic_cadence/services/analysis_service.py` passam a depender da porta `SongProvider`; `utils/encoding.py` e `infra/utils.py` migram para `cifra_core`.
- **Código (scraper)**: `app/utils/encoding.py`, `app/domain/cifra_utils.py` migram/consomem `cifra_core`; rotas Flask permanecem (`/api/...`).
- **Empacotamento**: migração de Poetry (analyzer) e pip/`requirements.txt` (scraper) para **`uv` workspaces**; um `pyproject` raiz + `uv.lock`, `docker-compose` e scripts únicos.
- **Contrato de dados**: o JSON da música passa a ser o modelo tipado `Cifra` (`artist, name, cifra[], cifra_html, youtube_url, cifraclub_url`) e as listagens o `SongRef` (`name, slug, url, only_lyrics`), de posse do `cifra_core` — não mais dicts soltos.
- **Documentação**: READMEs dos dois lados precisam ser corrigidos (Selenium→BeautifulSoup, `requirements.txt`/Poetry→`uv`, rotas `/api`, `python -m cli.main`→`harmonic`).
