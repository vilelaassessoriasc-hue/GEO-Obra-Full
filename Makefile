SHELL := /bin/bash

.DEFAULT_GOAL := help

help: ## Lista comandos
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | awk 'BEGIN {FS := ":.*?## "}; {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}'

env-prod: ## Gera .env.prod (se não existir)
	@[ -f .env.prod ] && echo '.env.prod já existe' || cp /mnt/data/.env.prod .env.prod && echo 'Criado .env.prod (edite os segredos).'

up: ## Sobe stack produção (db + api)
	docker compose -f docker-compose.prod.yml up --build

down: ## Derruba stack
	docker compose -f docker-compose.prod.yml down

migrate: ## Roda migrações Alembic
	docker compose -f docker-compose.prod.yml exec api alembic upgrade head

psql: ## Acessa psql no container
	docker compose -f docker-compose.prod.yml exec db psql -U postgres -d geoobra

openapi: ## Exporta OpenAPI para openapi.json e gera redoc.html (local)
	python scripts/export_openapi.py

test: ## Roda testes
	pytest -q
