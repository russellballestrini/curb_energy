.PHONY: help install install-dev install-server install-all
.PHONY: test test-unit test-integration test-functional test-all test-coverage
.PHONY: lint format type-check quality check
.PHONY: clean clean-pyc clean-test clean-build clean-all
.PHONY: venv venv-create venv-clean
.PHONY: server server-dev server-prod
.PHONY: build publish docs
.DEFAULT_GOAL := help

# Python and virtual environment configuration
PYTHON := python3
VENV := .venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip
PYTEST := $(VENV_BIN)/pytest
BLACK := $(VENV_BIN)/black
RUFF := $(VENV_BIN)/ruff
MYPY := $(VENV_BIN)/mypy
UVICORN := $(VENV_BIN)/uvicorn

# Project configuration
PROJECT_NAME := curb_energy
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m
COLOR_CYAN := \033[36m

# =============================================================================
# Help
# =============================================================================

help: ## Show this help message
	@echo "$(COLOR_BOLD)$(COLOR_BLUE)Curb Energy - Makefile Commands$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Environment Setup:$(COLOR_RESET)"
	@grep -E '^(venv|install).*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Testing:$(COLOR_RESET)"
	@grep -E '^test.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Code Quality:$(COLOR_RESET)"
	@grep -E '^(lint|format|type-check|quality|check).*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Server:$(COLOR_RESET)"
	@grep -E '^server.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Build & Deploy:$(COLOR_RESET)"
	@grep -E '^(build|publish|docs).*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Cleanup:$(COLOR_RESET)"
	@grep -E '^clean.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_CYAN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'

# =============================================================================
# Virtual Environment
# =============================================================================

venv: venv-create ## Create virtual environment and install dependencies
	@echo "$(COLOR_GREEN)✓ Virtual environment ready$(COLOR_RESET)"

venv-create: ## Create a new virtual environment
	@echo "$(COLOR_BLUE)Creating virtual environment...$(COLOR_RESET)"
	@test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	@$(PIP) install --upgrade pip setuptools wheel
	@echo "$(COLOR_GREEN)✓ Virtual environment created at $(VENV)$(COLOR_RESET)"

venv-clean: ## Remove virtual environment
	@echo "$(COLOR_YELLOW)Removing virtual environment...$(COLOR_RESET)"
	@rm -rf $(VENV)
	@echo "$(COLOR_GREEN)✓ Virtual environment removed$(COLOR_RESET)"

# =============================================================================
# Installation
# =============================================================================

install: venv-create ## Install core package dependencies
	@echo "$(COLOR_BLUE)Installing core dependencies...$(COLOR_RESET)"
	@$(PIP) install -e .
	@echo "$(COLOR_GREEN)✓ Core dependencies installed$(COLOR_RESET)"

install-dev: venv-create ## Install development dependencies
	@echo "$(COLOR_BLUE)Installing development dependencies...$(COLOR_RESET)"
	@$(PIP) install -e ".[dev]"
	@echo "$(COLOR_GREEN)✓ Development dependencies installed$(COLOR_RESET)"

install-server: venv-create ## Install server dependencies
	@echo "$(COLOR_BLUE)Installing server dependencies...$(COLOR_RESET)"
	@$(PIP) install -e ".[server]"
	@echo "$(COLOR_GREEN)✓ Server dependencies installed$(COLOR_RESET)"

install-all: venv-create ## Install all dependencies (core, server, dev, docs)
	@echo "$(COLOR_BLUE)Installing all dependencies...$(COLOR_RESET)"
	@$(PIP) install -e ".[all]"
	@echo "$(COLOR_GREEN)✓ All dependencies installed$(COLOR_RESET)"

# =============================================================================
# Testing
# =============================================================================

test: test-unit test-integration ## Run unit and integration tests (default)

test-unit: install-dev ## Run unit tests only
	@echo "$(COLOR_BLUE)Running unit tests...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/unit/ -v --tb=short
	@echo "$(COLOR_GREEN)✓ Unit tests completed$(COLOR_RESET)"

test-integration: install-dev install-server ## Run integration tests only
	@echo "$(COLOR_BLUE)Running integration tests...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/integration/ -v --tb=short
	@echo "$(COLOR_GREEN)✓ Integration tests completed$(COLOR_RESET)"

test-functional: install-dev install-server ## Run functional/E2E tests (requires running server)
	@echo "$(COLOR_YELLOW)Running functional tests...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Note: These tests require a running server and valid credentials$(COLOR_RESET)"
	@RUN_FUNCTIONAL_TESTS=true $(PYTEST) $(TEST_DIR)/functional/ -v --tb=short
	@echo "$(COLOR_GREEN)✓ Functional tests completed$(COLOR_RESET)"

test-client: install-dev ## Run existing client tests
	@echo "$(COLOR_BLUE)Running client tests...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/client/ -v --tb=short
	@echo "$(COLOR_GREEN)✓ Client tests completed$(COLOR_RESET)"

test-all: install-dev install-server ## Run all tests (unit, integration, client)
	@echo "$(COLOR_BLUE)Running all tests...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/ -v --tb=short \
		--ignore=$(TEST_DIR)/functional/
	@echo "$(COLOR_GREEN)✓ All tests completed$(COLOR_RESET)"

test-coverage: install-dev install-server ## Run tests with coverage report
	@echo "$(COLOR_BLUE)Running tests with coverage...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/ \
		--ignore=$(TEST_DIR)/functional/ \
		--cov=$(SRC_DIR)/$(PROJECT_NAME) \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=xml \
		-v
	@echo "$(COLOR_GREEN)✓ Coverage report generated in htmlcov/$(COLOR_RESET)"

test-watch: install-dev ## Run tests in watch mode (requires pytest-watch)
	@$(PIP) install pytest-watch
	@$(VENV_BIN)/ptw $(TEST_DIR)/ -- -v

# =============================================================================
# Code Quality
# =============================================================================

lint: install-dev ## Run linting checks (ruff)
	@echo "$(COLOR_BLUE)Running linting checks...$(COLOR_RESET)"
	@$(RUFF) check $(SRC_DIR) $(TEST_DIR)
	@echo "$(COLOR_GREEN)✓ Linting passed$(COLOR_RESET)"

format: install-dev ## Format code with black
	@echo "$(COLOR_BLUE)Formatting code...$(COLOR_RESET)"
	@$(BLACK) $(SRC_DIR) $(TEST_DIR)
	@echo "$(COLOR_GREEN)✓ Code formatted$(COLOR_RESET)"

format-check: install-dev ## Check if code is formatted (no changes)
	@echo "$(COLOR_BLUE)Checking code formatting...$(COLOR_RESET)"
	@$(BLACK) --check $(SRC_DIR) $(TEST_DIR)
	@echo "$(COLOR_GREEN)✓ Code formatting OK$(COLOR_RESET)"

type-check: install-dev ## Run type checking with mypy
	@echo "$(COLOR_BLUE)Running type checks...$(COLOR_RESET)"
	@$(MYPY) $(SRC_DIR)/$(PROJECT_NAME) --ignore-missing-imports || true
	@echo "$(COLOR_GREEN)✓ Type checking completed$(COLOR_RESET)"

quality: format-check lint type-check ## Run all quality checks (format, lint, type)
	@echo "$(COLOR_GREEN)✓ All quality checks passed$(COLOR_RESET)"

check: quality test ## Run all quality checks and tests
	@echo "$(COLOR_GREEN)✓ All checks passed$(COLOR_RESET)"

# =============================================================================
# Server
# =============================================================================

server: install-server ## Start the API server (development mode)
	@echo "$(COLOR_BLUE)Starting Curb Energy API server...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Server will be available at http://localhost:8000$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)API docs at http://localhost:8000/docs$(COLOR_RESET)"
	@$(UVICORN) $(PROJECT_NAME).server:app --reload --host 0.0.0.0 --port 8000

server-dev: install-server ## Start server with debug logging
	@echo "$(COLOR_BLUE)Starting server in debug mode...$(COLOR_RESET)"
	@$(UVICORN) $(PROJECT_NAME).server:app --reload --host 0.0.0.0 --port 8000 --log-level debug

server-prod: install-server ## Start server in production mode (no reload)
	@echo "$(COLOR_BLUE)Starting server in production mode...$(COLOR_RESET)"
	@$(UVICORN) $(PROJECT_NAME).server:app --host 0.0.0.0 --port 8000 --workers 4

server-test: install-server ## Start server for testing on port 8001
	@echo "$(COLOR_BLUE)Starting test server on port 8001...$(COLOR_RESET)"
	@$(UVICORN) $(PROJECT_NAME).server:app --reload --host 127.0.0.1 --port 8001

# =============================================================================
# Build & Publish
# =============================================================================

build: clean-build install-all ## Build distribution packages
	@echo "$(COLOR_BLUE)Building distribution packages...$(COLOR_RESET)"
	@$(PYTHON_VENV) -m pip install --upgrade build
	@$(PYTHON_VENV) -m build
	@echo "$(COLOR_GREEN)✓ Distribution packages built in dist/$(COLOR_RESET)"

publish: build ## Publish package to PyPI (requires credentials)
	@echo "$(COLOR_YELLOW)Publishing to PyPI...$(COLOR_RESET)"
	@$(PYTHON_VENV) -m pip install --upgrade twine
	@$(PYTHON_VENV) -m twine upload dist/*
	@echo "$(COLOR_GREEN)✓ Package published to PyPI$(COLOR_RESET)"

publish-test: build ## Publish to TestPyPI
	@echo "$(COLOR_YELLOW)Publishing to TestPyPI...$(COLOR_RESET)"
	@$(PYTHON_VENV) -m pip install --upgrade twine
	@$(PYTHON_VENV) -m twine upload --repository testpypi dist/*
	@echo "$(COLOR_GREEN)✓ Package published to TestPyPI$(COLOR_RESET)"

docs: install-all ## Build documentation
	@echo "$(COLOR_BLUE)Building documentation...$(COLOR_RESET)"
	@cd $(DOCS_DIR) && $(MAKE) html
	@echo "$(COLOR_GREEN)✓ Documentation built in $(DOCS_DIR)/_build/html/$(COLOR_RESET)"

docs-serve: docs ## Build and serve documentation locally
	@echo "$(COLOR_BLUE)Serving documentation at http://localhost:8080$(COLOR_RESET)"
	@cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server 8080

# =============================================================================
# Cleanup
# =============================================================================

clean: clean-pyc clean-test ## Remove Python artifacts and test cache

clean-pyc: ## Remove Python cache files
	@echo "$(COLOR_YELLOW)Removing Python cache files...$(COLOR_RESET)"
	@find . -type f -name '*.py[co]' -delete
	@find . -type d -name '__pycache__' -delete
	@find . -type d -name '*.egg-info' -delete
	@echo "$(COLOR_GREEN)✓ Python cache cleaned$(COLOR_RESET)"

clean-test: ## Remove test and coverage artifacts
	@echo "$(COLOR_YELLOW)Removing test artifacts...$(COLOR_RESET)"
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf coverage.xml
	@rm -rf $(TEST_DIR)/results.xml
	@echo "$(COLOR_GREEN)✓ Test artifacts cleaned$(COLOR_RESET)"

clean-build: ## Remove build artifacts
	@echo "$(COLOR_YELLOW)Removing build artifacts...$(COLOR_RESET)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ Build artifacts cleaned$(COLOR_RESET)"

clean-docs: ## Remove built documentation
	@echo "$(COLOR_YELLOW)Removing documentation build...$(COLOR_RESET)"
	@cd $(DOCS_DIR) && $(MAKE) clean
	@echo "$(COLOR_GREEN)✓ Documentation cleaned$(COLOR_RESET)"

clean-all: clean clean-build clean-docs venv-clean ## Remove all generated files and venv
	@echo "$(COLOR_GREEN)✓ All artifacts cleaned$(COLOR_RESET)"

# =============================================================================
# Development Helpers
# =============================================================================

shell: install-dev ## Start interactive Python shell with package imported
	@$(PYTHON_VENV) -i -c "from $(PROJECT_NAME) import *; print('Curb Energy package imported')"

notebook: install-dev ## Start Jupyter notebook (installs jupyter if needed)
	@$(PIP) install jupyter
	@$(VENV_BIN)/jupyter notebook

requirements: ## Generate requirements.txt from pyproject.toml
	@echo "$(COLOR_BLUE)Generating requirements.txt...$(COLOR_RESET)"
	@$(PIP) install pip-tools
	@$(VENV_BIN)/pip-compile pyproject.toml --output-file requirements.txt
	@echo "$(COLOR_GREEN)✓ requirements.txt generated$(COLOR_RESET)"

upgrade-deps: install-all ## Upgrade all dependencies to latest versions
	@echo "$(COLOR_BLUE)Upgrading dependencies...$(COLOR_RESET)"
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install --upgrade -e ".[all]"
	@echo "$(COLOR_GREEN)✓ Dependencies upgraded$(COLOR_RESET)"

# =============================================================================
# Docker (optional)
# =============================================================================

docker-build: ## Build Docker image
	@echo "$(COLOR_BLUE)Building Docker image...$(COLOR_RESET)"
	@docker build -t $(PROJECT_NAME):latest .
	@echo "$(COLOR_GREEN)✓ Docker image built$(COLOR_RESET)"

docker-run: ## Run Docker container
	@echo "$(COLOR_BLUE)Running Docker container...$(COLOR_RESET)"
	@docker run -p 8000:8000 \
		-e CURB_USERNAME \
		-e CURB_PASSWORD \
		-e CURB_CLIENT_TOKEN \
		-e CURB_CLIENT_SECRET \
		$(PROJECT_NAME):latest

# =============================================================================
# CI/CD Helpers
# =============================================================================

ci-test: install-all ## Run tests in CI environment
	@echo "$(COLOR_BLUE)Running CI tests...$(COLOR_RESET)"
	@$(PYTEST) $(TEST_DIR)/ \
		--ignore=$(TEST_DIR)/functional/ \
		--cov=$(SRC_DIR)/$(PROJECT_NAME) \
		--cov-report=xml \
		--cov-report=term \
		--junit-xml=test-results.xml \
		-v

ci-quality: format-check lint ## Run quality checks in CI environment
	@echo "$(COLOR_GREEN)✓ CI quality checks passed$(COLOR_RESET)"

ci: ci-quality ci-test ## Run all CI checks (quality + tests)
	@echo "$(COLOR_GREEN)✓ All CI checks passed$(COLOR_RESET)"

# =============================================================================
# Information
# =============================================================================

info: ## Show project information
	@echo "$(COLOR_BOLD)Project Information$(COLOR_RESET)"
	@echo "  Name:         $(PROJECT_NAME)"
	@echo "  Python:       $$($(PYTHON_VENV) --version 2>&1 || echo 'Not installed')"
	@echo "  Venv:         $(VENV)"
	@echo "  Source:       $(SRC_DIR)"
	@echo "  Tests:        $(TEST_DIR)"
	@echo ""
	@echo "$(COLOR_BOLD)Installed Packages$(COLOR_RESET)"
	@$(PIP) list 2>/dev/null | head -n 20 || echo "Virtual environment not created"

status: ## Show environment status
	@echo "$(COLOR_BOLD)Environment Status$(COLOR_RESET)"
	@echo -n "  Virtual env:  "
	@test -d $(VENV) && echo "$(COLOR_GREEN)✓ exists$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ not created$(COLOR_RESET)"
	@echo -n "  Dependencies: "
	@test -f $(VENV_BIN)/pytest && echo "$(COLOR_GREEN)✓ installed$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ not installed$(COLOR_RESET)"
	@echo -n "  Server deps:  "
	@test -f $(VENV_BIN)/uvicorn && echo "$(COLOR_GREEN)✓ installed$(COLOR_RESET)" || echo "$(COLOR_YELLOW)✗ not installed$(COLOR_RESET)"

# =============================================================================
# Quick Start
# =============================================================================

quickstart: install-all test ## Quick start: install everything and run tests
	@echo ""
	@echo "$(COLOR_GREEN)$(COLOR_BOLD)✓ Quick start completed!$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Next steps:$(COLOR_RESET)"
	@echo "  1. Set environment variables for authentication:"
	@echo "     export CURB_USERNAME='your_username'"
	@echo "     export CURB_PASSWORD='your_password'"
	@echo "     export CURB_CLIENT_TOKEN='your_token'"
	@echo "     export CURB_CLIENT_SECRET='your_secret'"
	@echo ""
	@echo "  2. Start the server:"
	@echo "     $(COLOR_CYAN)make server$(COLOR_RESET)"
	@echo ""
	@echo "  3. Open the dashboard:"
	@echo "     http://localhost:8000"
	@echo ""
	@echo "Run '$(COLOR_CYAN)make help$(COLOR_RESET)' to see all available commands"
