# Harmonic Cadence

Análise harmônica automática de música popular brasileira: extrai acordes,
tonalidade, graus, funções harmônicas, cadências e progressões — a partir de
cifras do [Cifra Club](https://www.cifraclub.com.br) — e gera relatórios em
JSON, Markdown ou HTML.

Monorepo com dois deploys (um analisador CLI e um serviço de scraping) sobre um
núcleo compartilhado, gerenciado com [`uv` workspaces](https://docs.astral.sh/uv/).

## Arquitetura

```
cifraclub.com.br
     │  (HTML)
     ▼
┌──────────────────┐    SongProvider (porta)    ┌──────────────────────┐
│  cifra_scraper    │ ◀────────────────────────── │  harmonic_analysis    │
│  API Flask /api   │   in-process │ HTTP          │  domínio + CLI        │
│  BeautifulSoup    │   + cache (CachePolicy)      │  + relatórios         │
└──────────────────┘                             └──────────────────────┘
            └──────────────┬───────────────────────────────┘
                           ▼
                   ┌────────────────┐
                   │   cifra_core    │  encoding · filtro de linhas (idempotente)
                   │  (compartilhado)│  regex de acorde · Cifra/SongRef
                   │                 │  SongProvider · cache
                   └────────────────┘
```

A análise obtém cifras **exclusivamente** pela porta `SongProvider`, com dois
adaptadores intercambiáveis:

- **in-process** (padrão) — raspa no próprio processo, **sem subir servidor**;
- **HTTP** — fala com o serviço Flask em `:3000/api`.

Um decorator de cache (`CachePolicy`: `NETWORK_FIRST`/`CACHE_FIRST`/`CACHE_ONLY`/
`REFRESH`) adiciona persistência e modo offline.

## Layout

```
packages/
├── cifra_core/         # núcleo compartilhado (fonte única de verdade)
├── cifra_scraper/      # API Flask (BeautifulSoup) — serviço opcional
└── harmonic_analysis/  # domínio musical + CLI + relatórios
pyproject.toml          # workspace uv (members = packages/*)
Dockerfile · docker-compose.yml · Makefile
```

## Setup

Requer [`uv`](https://docs.astral.sh/uv/) e Python ≥ 3.12.

```bash
uv sync          # instala todos os pacotes do workspace
```

## Uso (CLI)

Por padrão a CLI analisa **sem precisar subir nenhum servidor** (provider
in-process):

```bash
uv run harmonic analyze "Djavan" "Sina"
uv run harmonic analyze "Tom Jobim" "Garota de Ipanema" --format html
uv run harmonic analyze "Djavan" --all --format markdown
```

### Seleção de provider e cache

| Flag | Efeito |
| --- | --- |
| `--provider inprocess` | raspa no processo, sem servidor (**padrão**) |
| `--provider http` | usa o serviço Flask (`--api-url` p/ outra URL) |
| `--offline` | prioriza o cache local (`CACHE_FIRST`) |
| `--refresh` | força nova busca e reescreve o cache (`REFRESH`) |
| `--no-cache` | desativa o cache |

```bash
# Analisar via serviço HTTP (requer o scraper no ar — ver abaixo)
uv run harmonic analyze "Djavan" "Sina" --provider http

# Trabalhar offline a partir do cache
uv run harmonic analyze "Djavan" "Sina" --offline
```

## Serviço de scraping (opcional)

Necessário apenas para `--provider http` ou para consumir a API diretamente.

```bash
make scraper                       # uv run gunicorn em :3000
# ou via container:
docker compose up                  # build + sobe o serviço

curl http://localhost:3000/api/artists/djavan/songs/sina
```

## Desenvolvimento

```bash
make test     # uv run pytest (toda a suíte)
make lint     # uv run ruff check packages
make build    # docker compose build (imagem do scraper)
```

## Estado e próximos passos

O conteúdo teórico (ancorado em Almir Chediak) está destilado, implementado e
testado. A frente atual é **precisão da detecção de tonalidade**. Veja
[`ROADMAP.md`](ROADMAP.md) para o estado, o baseline de acurácia
(`uv run python scripts/key_baseline.py`) e o próximo passo (Fase B). O fluxo de
trabalho usa **OpenSpec** (`openspec list`; changes arquivadas em
`openspec/changes/archive/`).
