"""Leitura dos dados do Fluxo SEV (Projeto 1) — módulo puro.

Fornece funções para carregar o JSON do fluxo (`fluxo-sev/data/`) e os
POPs vinculados (`fluxo-sev/data/pops/`), usadas pela home e pela API.
"""

from __future__ import annotations

import json
from pathlib import Path

from gerapop.models import PopData

MODELO_POP_REF = "pop-desembarque"

FLUXO_DATA_DIR = Path(__file__).resolve().parents[1] / "fluxo-sev" / "data"
FLUXO_FILE = FLUXO_DATA_DIR / "fluxo-desembarque.json"
FLUXO_POPS_DIR = FLUXO_DATA_DIR / "pops"


def carregar_fluxo(path: Path | None = None) -> dict | None:
    """Lê o JSON do fluxo; None quando inexistente ou inválido."""
    try:
        payload = json.loads((path or FLUXO_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def classificar_nos(fluxo: dict) -> tuple[list[dict], list[dict]]:
    """Separa (pendentes, gerados) — nós sem e com pop_ref, por etapa."""
    nos = sorted(fluxo.get("nos", []), key=lambda no: no.get("etapa", 0))
    pendentes = [no for no in nos if not no.get("pop_ref")]
    gerados = [no for no in nos if no.get("pop_ref")]
    return pendentes, gerados


def carregar_pop_fluxo(pop_ref: str) -> PopData | None:
    """Converte o JSON de `fluxo-sev/data/pops/<pop_ref>.json` em PopData."""
    path = FLUXO_POPS_DIR / f"{pop_ref}.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        return PopData(**payload["pop"])
    except (KeyError, TypeError):
        return None
