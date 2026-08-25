.PHONY: dev test lint api web docker-up docker-down

dev:
	docker compose up --build

api:
	cd backend && uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check app tests

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down -v
