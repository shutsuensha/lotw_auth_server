
## Local
run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

install:
	uv pip install -r requirements.txt

list:
	uv pip list

database:
	psql -U evalshine -d mydatabase33341

nginx:
	sudo systemctl restart nginx



## Before Prod
lint:
	uv run ruff check app

format:
	uv run ruff format app


## Prod
services-up:
	docker compose -f docker-compose-services.yaml up --build -d

services-down: 
	docker compose -f docker-compose-services.yaml down

api-up:
	docker compose -f docker-compose.yaml up --build -d

api-down:
	docker compose -f docker-compose.yaml down

api:
	docker compose -f docker-compose.yaml down && docker compose -f docker-compose.yaml up --build -d

api-migrate:
	docker compose exec backend alembic upgrade head

postgres-connect:
	docker compose exec postgres psql -U evalshine -d mydatabase33341 -c "SELECT * FROM alembic_version;"