.PHONY: up down logs build migrate test lint help

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build

migrate:
	docker-compose exec postgres psql -U blogin_user -d blogin -f /migrations/init.sql

psql:
	docker-compose exec postgres psql -U blogin_user -d blogin

test:
	@echo "Running tests for all services..."
	cd services/auth-service && python -m pytest || true
	cd services/user-service && python -m pytest || true
	cd services/post-service && python -m pytest || true
	cd services/comment-service && python -m pytest || true
	cd services/like-service && python -m pytest || true

lint:
	@echo "Running linters..."
	cd services/auth-service && ruff check . || true
	cd services/user-service && ruff check . || true
	cd services/post-service && ruff check . || true
	cd services/comment-service && ruff check . || true
	cd services/like-service && ruff check . || true

clean:
	docker-compose down -v
	docker system prune -f

help:
	@echo "Available commands:"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View service logs"
	@echo "  make build    - Build Docker images"
	@echo "  make migrate  - Run database migrations"
	@echo "  make psql     - Open PostgreSQL console"
	@echo "  make test     - Run all tests"
	@echo "  make lint     - Run code linters"
	@echo "  make clean    - Clean up containers and volumes"
