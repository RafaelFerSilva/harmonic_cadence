# cifra_scraper

API REST (Flask) que faz scraping de cifras do
[Cifra Club](https://www.cifraclub.com.br) e as devolve em JSON. Faz parte do
monorepo **Harmonic Cadence** e compartilha modelos e utilitários com
`cifra_core`.

O scraping usa **requests + BeautifulSoup (lxml)** — não há navegador nem
Selenium envolvidos.

## Como rodar

A partir da raiz do monorepo:

```bash
# Direto com uv (gunicorn em :3000)
make scraper

# Ou em container
docker compose up
```

## Endpoints

Todas as rotas ficam sob o prefixo `/api`:

```bash
# Cifra de uma música
curl http://localhost:3000/api/artists/coldplay/songs/the-scientist

# Lista de músicas de um artista
curl http://localhost:3000/api/artists/coldplay/songs
```

Exemplo de resposta de `/api/artists/:artist/songs/:song`:

```json
{
  "artist": "Coldplay",
  "name": "The Scientist",
  "cifra": ["C#m7  A9  E  E9", "..."],
  "cifra_html": "...",
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "cifraclub_url": "https://www.cifraclub.com.br/coldplay/the-scientist"
}
```

As linhas em `cifra` já vêm **limpas** (filtro canônico e idempotente do
`cifra_core`): sem tablaturas, marcadores de seção (`[Intro]`, `Parte N de M`,
`tom:`) nem duplicatas — preservando as linhas de acordes e de letra.

## Estrutura

```
src/cifra_scraper/
├── interface/http/      # rotas Flask (Blueprint, url_prefix=/api)
├── application/         # casos de uso
├── infrastructure/
│   ├── repositories/    # CifraClubRepository
│   └── scrapers/        # CifraClubScraper (requests + BeautifulSoup)
└── song_provider.py     # InProcessSongProvider (porta SongProvider)
```
