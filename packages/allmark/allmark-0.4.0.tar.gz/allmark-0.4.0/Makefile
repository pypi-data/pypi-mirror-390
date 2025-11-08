.PHONY: help install install-dev test lint format clean build

help:
	@echo "allmark - Development Commands"
	@echo ""
	@echo "  make install        Install package in current environment"
	@echo "  make install-dev    Install with pinned dev dependencies"
	@echo "  make test           Run tests with pytest"
	@echo "  make lint           Run linting (flake8 + mypy)"
	@echo "  make format         Format code with black"
	@echo "  make clean          Clean build artifacts"
	@echo "  make build          Build distribution packages"
	@echo ""

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest -v --cov=allmark --cov-report=term-missing

lint:
	flake8 src/allmark/
	mypy src/allmark/

format:
	black src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf src/*.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

build: clean
	python -m build
