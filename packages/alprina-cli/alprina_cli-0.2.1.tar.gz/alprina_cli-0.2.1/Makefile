.PHONY: help prepare install dev test lint format clean run

help:
	@echo "Alprina CLI - Makefile commands"
	@echo ""
	@echo "  prepare    - Set up development environment"
	@echo "  install    - Install package in development mode"
	@echo "  dev        - Install development dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters"
	@echo "  format     - Format code with black and isort"
	@echo "  clean      - Clean build artifacts"
	@echo "  run        - Run alprina CLI"
	@echo ""

prepare:
	@echo "Setting up development environment..."
	python -m venv venv
	@echo "✓ Virtual environment created"
	@echo "Activate with: source venv/bin/activate"

install:
	pip install -e .
	@echo "✓ Alprina CLI installed in development mode"

dev:
	pip install -e ".[dev]"
	@echo "✓ Development dependencies installed"

test:
	pytest

lint:
	flake8 src/
	pylint src/alprina_cli/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/
	@echo "✓ Code formatted"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned build artifacts"

run:
	alprina --help

.DEFAULT_GOAL := help
