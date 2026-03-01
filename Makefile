# pyRofex-to-Excel Project Makefile
# Provides convenient commands for common development tasks

.PHONY: help install install-dev check upgrade clean lint format type-check run test

# Default target
help:
	@echo "pyRofex-to-Excel Project Commands"
	@echo "============================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install     - Install package (editable)"
	@echo "  make install-dev - Install package + dev extras"
	@echo "  make check       - Validate environment"
	@echo "  make upgrade     - Upgrade pip tooling + reinstall"
	@echo "  make clean       - Clean virtual environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  make lint        - Run linting (ruff)"
	@echo "  make format      - Format code (ruff)"
	@echo "  make type-check  - Run type checking (mypy)"
	@echo "  make run         - Run the main application"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make config      - Run configuration migration"
	@echo "  make validate    - Validate system setup"

# Setup commands
install:
	@python -m pip install -e . --force-reinstall

install-dev:
	@python -m pip install -e ".[dev]" --force-reinstall

check:
	@python tools/validate_system.py

upgrade:
	@python -m pip install --upgrade pip setuptools wheel
	@python -m pip install -e ".[dev]" --upgrade --force-reinstall

clean:
	@echo "🧹 Removing .venv if present..."
	@rm -rf .venv || true

# Development commands  
lint:
	@echo "🔍 Running linter..."
	@ruff check .

format:
	@echo "🎨 Formatting code..."
	@ruff format .

type-check:
	@echo "🔍 Running type checker..."
	@mypy .

# Application commands
run:
	@echo "🚀 Running pyRofex-to-Excel..."
	@pyrofex-to-excel

config:
	@echo "⚙️ Running quickstart validation..."
	@python tools/validate_quickstart.py

validate:
	@echo "✅ Validating system setup..."
	@python tools/validate_system.py

# Combined quality checks
quality: lint type-check
	@echo "✅ All quality checks passed"

# Development setup with quality tools
dev-setup: install-dev
	@echo "🔧 Setting up pre-commit hooks..."
	@pre-commit install || echo "⚠️ pre-commit not available - install with: pip install pre-commit"
	@echo "✅ Development setup complete"