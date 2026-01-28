.PHONY: help up down logs migrate test seed

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Show logs from all services
	docker compose logs -f

migrate: ## Run database migrations
	docker compose exec backend alembic upgrade head

test: ## Run tests
	docker compose exec backend pytest

seed: ## Load initial data
	docker compose exec backend python scripts/seed_data.py
