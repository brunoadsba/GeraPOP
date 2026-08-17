.PHONY: help install install-dev run run-backend run-frontend test lint format backup clean docker-build docker-run

PYTHON ?= python3.11
UV ?= uv
VENV := .venv
BIN := $(VENV)/bin
STREAMLIT := $(BIN)/streamlit
PYTEST := $(BIN)/pytest
RUFF := $(BIN)/ruff
PYTHON_BIN := $(BIN)/python

help:
	@echo "Comandos disponíveis:"
	@echo "  make install      — cria venv (Python 3.11) e instala dependências"
	@echo "  make install-dev  — instala dependências + ferramentas de dev"
	@echo "  make run-backend  — sobe a API FastAPI em http://localhost:8000"
	@echo "  make run-frontend — sobe o frontend React em http://localhost:5173"
	@echo "  make run          — sobe backend + frontend em paralelo"
	@echo "  make test         — executa testes"
	@echo "  make lint         — verifica código com ruff"
	@echo "  make format       — formata código com ruff"
	@echo "  make backup       — gera zip com todos os POPs e o rascunho"
	@echo "  make clean        — remove venv e caches"
	@echo "  make docker-run   — sobe via Docker (alternativa ao venv local)"

$(VENV)/bin/python:
	$(UV) venv --python $(PYTHON) $(VENV)
	$(UV) pip install -r requirements.txt
	$(UV) pip install -e .

install: $(VENV)/bin/python

install-dev: install
	$(UV) pip install -r requirements-dev.txt

run-backend: install-dev
	$(PYTHON_BIN) -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

run-frontend:
	cd frontend && npm run dev

run: run-backend &
	cd frontend && npm run dev

test: install-dev
	$(PYTEST) -q

lint: install-dev
	$(RUFF) check app.py backend gerapop tests
	$(RUFF) format --check app.py backend gerapop tests

format: install-dev
	$(RUFF) format app.py backend gerapop tests
	$(RUFF) check --fix app.py backend gerapop tests

backup: install
	$(BIN)/python -m gerapop.backup

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker compose build

docker-run:
	docker compose up --build