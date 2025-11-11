# Graph Elements - Development Makefile
# Requires uv to be installed

.PHONY: help install test lint format type-check clean build publish dev-install

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync --all-extras

dev-install:  ## Install in development mode
	uv sync --all-extras
	uv pip install -e .

test:  ## Run tests with coverage
	uv run pytest

test-verbose:  ## Run tests with verbose output
	uv run pytest -v

coverage:  ## Generate coverage report
	uv run pytest --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:  ## Run all linting checks
	uv run ruff check .
	uv run black --check .
	uv run isort --check-only .
	uv run mypy graph_elements/

lint-fix:  ## Fix linting issues
	uv run ruff check --fix .
	uv run black .
	uv run isort .

format:  ## Format code (alias for lint-fix)
	$(MAKE) lint-fix

type-check:  ## Run type checking
	uv run mypy graph_elements/

security:  ## Run security checks
	uv run bandit -r graph_elements/
	uv run safety check

clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

build:  ## Build the package
	uv run python -m build

publish-test:  ## Publish to TestPyPI
	uv run python -m build
	uv run twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	uv run python -m build
	uv run twine upload dist/*

pre-commit:  ## Run pre-commit hooks
	uv run pre-commit run --all-files

update-deps:  ## Update dependencies
	uv lock --upgrade

check-all: lint test security  ## Run all checks

ci: install check-all  ## Run CI pipeline locally

# Development workflow commands
dev: dev-install  ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make lint' to check code quality"

# Quick commands for common workflows
qa: lint-fix test  ## Quick QA: format code and run tests

release-check: clean build  ## Check if ready for release
	uv run twine check dist/*
	@echo "Release check passed!"