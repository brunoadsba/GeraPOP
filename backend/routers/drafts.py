"""Rascunho persistente do formulário."""

from __future__ import annotations

from fastapi import APIRouter

from backend.schemas import DraftPayload
from gerapop.storage import clear_draft, get_draft, save_draft

router = APIRouter(prefix="/api/draft", tags=["draft"])


@router.get("", response_model=DraftPayload | None)
def obter_rascunho() -> DraftPayload | None:
    """Retorna o rascunho salvo (form + origem de edição)."""
    payload = get_draft()
    if payload is None:
        return None
    return DraftPayload(
        form=payload.get("form", {}),
        loaded_from_id=payload.get("loaded_from_id"),
    )


@router.put("")
def salvar_rascunho(payload: DraftPayload) -> dict:
    """Persiste o rascunho atual do formulário."""
    save_draft({"form": payload.form, "loaded_from_id": payload.loaded_from_id})
    return {"ok": True}


@router.delete("")
def limpar_rascunho() -> dict:
    """Remove o rascunho salvado."""
    clear_draft()
    return {"ok": True}
