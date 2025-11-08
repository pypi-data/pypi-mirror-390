.PHONY: help install test lint type-check format clean build

help:
	@echo "B8TeX Development Commands"
	@echo ""
	@echo "  install      Install dependencies with uv"
	@echo "  test         Run tests with pytest"
	@echo "  lint         Run ruff linter"
	@echo "  type-check   Run mypy type checker"
	@echo "  format       Format code with ruff"
	@echo "  clean        Remove build artifacts"
	@echo "  build        Build package"

install:
	uv sync --dev

test:
	uv run pytest

test-cov:
	uv run pytest --cov=b8tex --cov-report=html --cov-report=term

lint:
	uv run ruff check src tests

lint-fix:
	uv run ruff check --fix src tests

type-check:
	uv run mypy src/b8tex

format:
	uv run ruff format src tests

format-check:
	uv run ruff format --check src tests

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	uv build

all: install lint type-check test

.DEFAULT_GOAL := help
