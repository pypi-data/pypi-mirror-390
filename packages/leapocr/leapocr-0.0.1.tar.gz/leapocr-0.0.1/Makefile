.PHONY: help install dev-install clean generate format lint type-check test test-cov test-integration run-example build publish

# Default target
help:
	@echo "LeapOCR Python SDK - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install          Install production dependencies"
	@echo "  make dev-install      Install all dependencies including dev tools"
	@echo ""
	@echo "Code Generation:"
	@echo "  make fetch-spec       Download OpenAPI spec from API"
	@echo "  make generate         Generate client from OpenAPI spec"
	@echo "  make regenerate       Fetch + generate (full refresh)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format           Format code with ruff"
	@echo "  make lint             Lint code with ruff"
	@echo "  make type-check       Type check with mypy"
	@echo "  make check            Run format + lint + type-check"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run unit tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make test-integration Run integration tests (requires API key)"
	@echo "  make test-all         Run all tests"
	@echo ""
	@echo "Build & Publish:"
	@echo "  make build            Build distribution packages"
	@echo "  make publish          Publish to PyPI (requires credentials)"
	@echo "  make publish-test     Publish to TestPyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean            Remove generated files and caches"
	@echo "  make run-example      Run basic example"

# Setup & Installation
install:
	uv sync --no-dev

dev-install:
	uv sync

# Code Generation
fetch-spec:
	@echo "Downloading OpenAPI spec from API..."
	curl -s -o openapi.json http://localhost:8080/api/v1/docs/openapi.json
	@echo "✓ Downloaded to openapi.json"

generate: openapi.json
	@echo "Checking for openapi-generator-cli..."
	@command -v openapi-generator-cli >/dev/null 2>&1 || { \
		echo "Error: openapi-generator-cli not found"; \
		echo "Install with: npm install -g @openapitools/openapi-generator-cli"; \
		echo "Or using Homebrew: brew install openapi-generator"; \
		exit 1; \
	}
	@echo "Setting up Java environment..."
	@eval "$$(mise env -s bash)" && java -version
	@echo "Generating Python client from OpenAPI spec..."
	@rm -rf leapocr/generated
	@eval "$$(mise env -s bash)" && openapi-generator-cli generate \
		-i openapi.json \
		-g python-pydantic-v1 \
		-o leapocr/generated \
		--skip-validate-spec \
		--additional-properties=\
packageName=leapocr.generated,\
projectName=leapocr-generated,\
packageVersion=0.1.0,\
library=asyncio,\
useOneOfDiscriminatorLookup=true,\
generateSourceCodeOnly=true \
		--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false
	@echo "✓ Generated client in leapocr/generated/"

regenerate: fetch-spec generate
	@echo "✓ Full regeneration complete"

# Code Quality
format:
	@echo "Formatting code with ruff..."
	uv run ruff format .

lint:
	@echo "Linting code with ruff..."
	uv run ruff check .

lint-fix:
	@echo "Linting and fixing code with ruff..."
	uv run ruff check --fix .

type-check:
	@echo "Type checking with mypy..."
	uv run mypy leapocr/

check: format lint type-check
	@echo "✓ All checks passed"

# Testing
test:
	@echo "Running unit tests..."
	uv run pytest tests/ -v --ignore=tests/integration

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest tests/ --ignore=tests/integration --cov=leapocr --cov-report=html --cov-report=term

test-integration:
	@echo "Running integration tests..."
	@if [ -z "$$LEAPOCR_API_KEY" ]; then \
		echo "Error: LEAPOCR_API_KEY environment variable not set"; \
		exit 1; \
	fi
	uv run pytest tests/integration/ -v

test-all: test test-integration

# Build & Publish
build:
	@echo "Building distribution packages..."
	uv build

publish: build
	@echo "Publishing to PyPI..."
	uv publish

publish-test: build
	@echo "Publishing to TestPyPI..."
	uv publish --publish-url https://test.pypi.org/legacy/

# Utilities
clean:
	@echo "Cleaning generated files and caches..."
	rm -rf leapocr/generated
	rm -rf openapi.json
	rm -rf .venv
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned"

run-example:
	@echo "Running basic example..."
	@if [ -z "$$LEAPOCR_API_KEY" ]; then \
		echo "Error: LEAPOCR_API_KEY environment variable not set"; \
		echo "Set it with: export LEAPOCR_API_KEY=your-api-key"; \
		exit 1; \
	fi
	uv run python examples/basic_usage.py

# Version management
version:
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

.DEFAULT_GOAL := help
