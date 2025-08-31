# Virtual environment Python path
VENV_PYTHON = .venv/bin/python
VENV_PIP = .venv/bin/pip

.PHONY: help install test type-check clean build run

help:
	@echo "Available targets:"
	@echo "  install      - Install package"
	@echo "  test         - Run tests"
	@echo "  type-check   - Run type checking with mypy"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  run          - Run the application"

install:
	$(VENV_PIP) install -e .[dev]

test:
	$(VENV_PYTHON) -m pytest -v --cov=.

type-check:
	$(VENV_PYTHON) -m mypy .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:
	$(VENV_PYTHON) -m build

run:
	$(VENV_PYTHON) run.py
