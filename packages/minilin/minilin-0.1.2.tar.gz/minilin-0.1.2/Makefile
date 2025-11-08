.PHONY: install test lint format clean build upload

install:
	pip install -e ".[dev,all]"

test:
	pytest tests/ -v --cov=minilin

lint:
	flake8 minilin tests examples
	mypy minilin

format:
	black minilin tests examples

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

help:
	@echo "Available commands:"
	@echo "  make install  - Install package in development mode"
	@echo "  make test     - Run tests with coverage"
	@echo "  make lint     - Run linters"
	@echo "  make format   - Format code with black"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make build    - Build distribution packages"
	@echo "  make upload   - Upload to PyPI"
