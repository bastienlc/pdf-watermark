UV := uv
RUFF := uv run ruff
PYTEST := uv run pytest

.PHONY: help install-ci install lint test build

help:
	@echo "Available targets:"
	@echo "  install-ci   - Install project for CI"
	@echo "  install      - Install project for development"
	@echo "  lint         - Run the linter (ruff)"
	@echo "  test         - Run the tests (pytest)"
	@echo "  build        - Build the release version of the project"

install-ci:
	@echo "Installing project..."
	$(UV) sync

install:
	@echo "Installing project..."
	$(UV) sync
	uv run pre-commit install

lint:
	@echo "Running linter..."
	$(RUFF) check .

test:
	@echo "Running tests..."
	$(PYTEST) --cov=src --cov-report=xml --cov-report=html

build:
	@echo "Building package..."
	$(UV) build
