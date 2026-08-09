.PHONY: help install install-dev run test lint format clean docker-build docker-run

PYTHON ?= python3.11
UV ?= uv
VENV := .venv
BIN := $(VENV)/bin
STREAMLIT := $(BIN)/streamlit
PYTEST := $(BIN)/pytest
RUFF := $(BIN)/ruff

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      — cria venv (Python 3.11) e instala dependências"
	@echo "  make install-dev  — instala dependências + ferramentas de dev"
	@echo "  make run          — sobe o app Streamlit em http://localhost:8501"
	@echo "  make test         — executa testes"
	@echo "  make lint         — verifica código com ruff"
	@echo "  make format       — formata código com ruff"
	@echo "  make clean        — remove venv e caches"
	@echo "  make docker-run   — sobe via Docker (alternativa ao venv local)"

$(VENV)/bin/python:
	$(UV) venv --python $(PYTHON) $(VENV)
	$(UV) pip install -r requirements.txt
	$(UV) pip install -e .

install: $(VENV)/bin/python

install-dev: install
	$(UV) pip install -r requirements-dev.txt

run: install
	$(STREAMLIT) run app.py --server.headless true

test: install-dev
	$(PYTEST) -q

lint: install-dev
	$(RUFF) check app.py gerapop tests
	$(RUFF) format --check app.py gerapop tests

format: install-dev
	$(RUFF) format app.py gerapop tests
	$(RUFF) check --fix app.py gerapop tests

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker compose build

docker-run:
	docker compose up --build
