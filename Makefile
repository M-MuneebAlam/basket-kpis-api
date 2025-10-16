.PHONY: install run dev test lint docker-build docker-run docker-clean docker-evaluate

# Local development
install:
	pip install -r requirements.txt

run:
	uvicorn main:app --host 0.0.0.0 --port 8000

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v test_api.py

lint:
	ruff check main.py test_api.py

# Docker commands
docker-build:
	docker build -t basket-kpis-api .

docker-run:
	docker run -p 8000:8000 --name basket-kpis basket-kpis-api

docker-clean:
	docker stop basket-kpis || true
	docker rm basket-kpis || true

# Complete evaluation workflow
docker-evaluate:
	docker build -t basket-kpis-api .
	docker run --rm basket-kpis-api pytest test_api.py -v
	docker run --rm basket-kpis-api ruff check main.py test_api.py
	docker run -d -p 8000:8000 --name basket-kpis basket-kpis-api
	@echo "Application running at http://localhost:8000"