# Imagem do serviço de scraping (cifra_scraper) — build a partir da raiz do
# monorepo para que o uv enxergue o workspace (cifra-core é dependência).
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
COPY . /app

# Instala apenas o pacote do scraper e suas dependências (inclui cifra-core).
RUN uv sync --frozen --package cifra-scraper --no-dev

EXPOSE 3000

CMD ["uv", "run", "--no-sync", "--package", "cifra-scraper", \
     "gunicorn", "-b", "0.0.0.0:3000", "cifra_scraper:create_app()"]
