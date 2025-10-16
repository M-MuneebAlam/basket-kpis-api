.PHONY: install run dev test lint format docker-build docker-run docker-clean clean help

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

format:
	ruff format main.py test_api.py

docker-build:
	docker build -t basket-kpis-api .

docker-run:
	docker run -p 8000:8000 --name basket-kpis basket-kpis-api

docker-clean:
	docker stop basket-kpis || true
	docker rm basket-kpis || true

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.log" -delete 2>/dev/null || true

help:
	@echo "Available targets:"
	@echo "  install      - Install Python dependencies"
	@echo "  run          - Run the application (production mode)"
	@echo "  dev          - Run the application (development mode with reload)"
	@echo "  test         - Run tests"
	@echo "  lint         - Check code with ruff"
	@echo "  format       - Format code with ruff"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker container"
	@echo "  docker-clean - Stop and remove Docker container"
	@echo "  clean        - Clean up cache files and logs"
	@echo "  help         - Show this help message"