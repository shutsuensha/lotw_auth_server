
nginx:
	sudo systemctl restart nginx

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

install:
	uv pip install -r requirements.txt -r requirements-dev.txt

list:
	uv pip list

sync: ## Синхронизировать окружение по lock-файлу (ci/cd)
	uv pip sync requirements.lock.txt

lock:
	uv pip freeze > requirements.lock.txt

lint:
	uv run ruff check app

format:
	uv run ruff format app

typecheck:
	uv run mypy app

security-bandit: ## Поиск уязвимостей в коде (Bandit)
	uv run bandit -r app -ll -q

security-safety: ## Проверка зависимостей по CVE (Safety)
	uv run safety check --full-report

security-audit: ## Альтернатива Safety — pip-audit
	uv run pip-audit

security-check: 
	security-bandit security-safety security-audit ## Запустить все проверки безопасности

# Создать новую миграцию: make revision name=название
revision:
	uv run alembic revision --autogenerate -m "$(name)"

# Применить миграции
upgrade:
	uv run alembic upgrade head

# Сделать миграцию и сразу применить: make migrate name=название
migrate: 
	revision upgrade

database:
	psql -U evalshine -d auth_db_3333



services-up:
	docker-compose -f docker-compose-services.yaml up --build -d

services-down: 
	docker-compose -f docker-compose-services.yaml down

api-up:
	docker-compose -f docker-compose.yaml up --build -d

api-down:
	docker-compose -f docker-compose.yaml down

api:
	docker-compose -f docker-compose.yaml down && docker-compose -f docker-compose.yaml up --build -d

api-migrate:
	docker exec -it backend alembic upgrade head

postgres-connect:
	docker exec -it postgres psql -U postgres -d game_server_new -c "SELECT * FROM alembic_version;"
