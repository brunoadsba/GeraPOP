.PHONY: help install install-dev run run-backend run-frontend test lint format backup clean docker-build docker-run

PYTHON ?= python3.11
UV ?= uv
VENV := .venv

ifeq ($(OS),Windows_NT)
BIN := $(VENV)/Scripts
PYTHON_BIN := $(BIN)/python.exe
PYTEST := $(BIN)/pytest.exe
RUFF := $(BIN)/ruff.exe
STREAMLIT := $(BIN)/streamlit.exe
PYTHON ?= 3.11
CLEAN_CMD = powershell -NoProfile -Command "Remove-Item -Recurse -Force $(VENV),.pytest_cache,.ruff_cache,.mypy_cache -ErrorAction SilentlyContinue; Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force"
BACKEND_START = powershell -NoProfile -Command "Start-Process '$(PYTHON_BIN)' -ArgumentList '-m','uvicorn','backend.main:app','--reload','--host','127.0.0.1','--port','8000'"
else
BIN := $(VENV)/bin
PYTHON_BIN := $(BIN)/python
PYTEST := $(BIN)/pytest
RUFF := $(BIN)/ruff
STREAMLIT := $(BIN)/streamlit
CLEAN_CMD = rm -rf $(VENV) .pytest_cache .ruff_cache .mypy_cache; find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
BACKEND_START = $(PYTHON_BIN) -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 &
endif

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

$(PYTHON_BIN):
	$(UV) venv --python $(PYTHON) $(VENV)
	$(UV) pip install -r requirements.txt
	$(UV) pip install -e .

install: $(PYTHON_BIN)

install-dev: install
	$(UV) pip install -r requirements-dev.txt

run-backend: install-dev
	$(PYTHON_BIN) -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

run-frontend:
	cd frontend && npm run dev

run: 
	$(BACKEND_START)
	cd frontend && npm run dev

test: install-dev
	$(PYTEST) -q

lint: install-dev
	$(RUFF) check app.py backend gerapop tests scripts
	$(RUFF) format --check app.py backend gerapop tests scripts

format: install-dev
	$(RUFF) format app.py backend gerapop tests scripts
	$(RUFF) check --fix app.py backend gerapop tests scripts

backup: install
	$(PYTHON_BIN) -m gerapop.backup

clean:
	$(CLEAN_CMD)

docker-build:
	docker compose build

docker-run:
	docker compose up --build