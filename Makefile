.PHONY: install scraper analyze test lint build up

install:           ## Instala o workspace (todos os pacotes)
	uv sync

scraper:           ## Sobe o serviço de scraping em :3000/api
	uv run --package cifra-scraper gunicorn -b 0.0.0.0:3000 "cifra_scraper:create_app()"

analyze:           ## Ex.: make analyze ARGS='"Djavan" "Sina"'
	uv run harmonic analyze $(ARGS)

test:              ## Roda toda a suíte
	uv run pytest

lint:              ## Lint com ruff
	uv run ruff check packages

build:             ## Build da imagem do scraper
	docker compose build

up:                ## Sobe o scraper via docker compose
	docker compose up
