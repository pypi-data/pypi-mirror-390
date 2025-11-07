.PHONY: help install install-dev test test-cov lint format type-check security clean build publish docs

help: ## Show this help message
	@echo "vCon WTF - Development Commands"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	uv sync

install-dev: ## Install development dependencies
	uv sync --dev

install-integration: ## Install integration dependencies
	uv sync --dev --group integration

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ --cov=src/wtf_transcript_converter --cov-report=html --cov-report=term-missing

test-integration: ## Run integration tests
	uv run pytest tests/test_integration/ -v

test-cross-provider: ## Run cross-provider tests
	uv run pytest tests/test_cross_provider/ -v

test-all: ## Run all tests
	uv run pytest tests/ -v --tb=short

lint: ## Run linting
	uv run python -m flake8 src tests --max-line-length=99 --extend-ignore=E203,W503,E501,F401,D107,D200,D401,D403,B007,B017,F541,F841,E402,E712
	uv run python -m black --check src tests
	uv run python -m isort --check-only src tests

format: ## Format code
	uv run python -m black src tests
	uv run python -m isort src tests

type-check: ## Run type checking
	uv run python -m mypy src

security: ## Run security checks
	uv run python -m bandit -r src/ -f json -o bandit-report.json
	uv run python -m safety check

pre-commit: ## Run pre-commit hooks
	uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	uv run pre-commit install

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	uv build

publish-test: ## Publish to TestPyPI
	uv build
	uv run twine upload --repository testpypi dist/*

publish: ## Publish to PyPI
	uv build
	uv run twine upload dist/*

docs: ## Build documentation
	cd docs && uv run sphinx-build -b html . _build/html

docs-clean: ## Clean documentation build
	cd docs && rm -rf _build/

docs-serve: ## Serve documentation locally
	cd docs/_build/html && uv run python -m http.server 8000

ci-test: ## Run CI test suite
	uv run pytest tests/ --cov=src/wtf_transcript_converter --cov-report=xml --cov-report=html
	uv run pytest tests/test_integration/ -v --tb=short
	uv run pytest tests/test_cross_provider/ -v --tb=short

ci-lint: ## Run CI linting
	uv run python -m black --check src tests
	uv run python -m isort --check-only src tests
	uv run python -m flake8 src tests --max-line-length=99 --extend-ignore=E203,W503,E501,F401,D107,D200,D401,D403,B007,B017,F541,F841,E402,E712
	uv run python -m mypy src

ci-security: ## Run CI security checks
	uv run bandit -r src/ -f json -o bandit-report.json

ci-build: ## Run CI build
	uv build

cross-provider-test: ## Run cross-provider consistency test
	uv run vcon-wtf cross-provider consistency tests/fixtures/whisper_sample.json --verbose

cross-provider-performance: ## Run cross-provider performance test
	uv run vcon-wtf cross-provider performance tests/fixtures/whisper_sample.json --iterations 3

cross-provider-quality: ## Run cross-provider quality test
	uv run vcon-wtf cross-provider quality tests/fixtures/whisper_sample.json --verbose

cross-provider-all: ## Run all cross-provider tests
	uv run vcon-wtf cross-provider all tests/fixtures/whisper_sample.json --output-dir reports/

setup-dev: install-dev pre-commit-install ## Set up development environment
	@echo "Development environment set up complete!"
	@echo "Run 'make test' to verify everything is working."

release-check: ## Check if ready for release
	@echo "Checking release readiness..."
	@make lint
	@make type-check
	@make security
	@make test-all
	@make build
	@echo "✅ Ready for release!"

# Development workflow shortcuts
dev-setup: setup-dev ## Alias for setup-dev
check: lint type-check security ## Run all checks
full-test: test-all cross-provider-all ## Run complete test suite
