.PHONY: install run dev test lint format docker-build docker-run docker-clean docker-test docker-lint docker-all-tests docker-evaluate clean help

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

docker-test:
	docker run --rm basket-kpis-api pytest test_api.py -v

docker-lint:
	docker run --rm basket-kpis-api ruff check main.py test_api.py

docker-all-tests:
	docker run --rm basket-kpis-api sh -c "pytest test_api.py -v && ruff check main.py test_api.py"

docker-evaluate:
	@echo "🔨 Building Docker image..."
	docker build -t basket-kpis-api .
	@echo "🧪 Running tests in container..."
	docker run --rm basket-kpis-api pytest test_api.py -v
	@echo "🔍 Checking code quality..."
	docker run --rm basket-kpis-api ruff check main.py test_api.py
	@echo "🚀 Starting application..."
	docker run -d -p 8000:8000 --name basket-kpis basket-kpis-api
	@echo "✅ Application running at http://localhost:8000"
	@echo "📚 API docs available at http://localhost:8000/docs"
	@echo "🧹 Use 'make docker-clean' to stop and remove container"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.log" -delete 2>/dev/null || true

help:
	@echo "Available targets:"
	@echo "  install        - Install Python dependencies"
	@echo "  run            - Run the application (production mode)"
	@echo "  dev            - Run the application (development mode with reload)"
	@echo "  test           - Run tests locally"
	@echo "  lint           - Check code with ruff locally"
	@echo "  format         - Format code with ruff"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-test    - Run tests in Docker container"
	@echo "  docker-lint    - Run linting in Docker container"
	@echo "  docker-all-tests - Run tests and linting in Docker"
	@echo "  docker-evaluate - Complete evaluation: build, test, lint, and run"
	@echo "  docker-clean   - Stop and remove Docker container"
	@echo "  clean          - Clean up cache files and logs"
	@echo "  help           - Show this help message"