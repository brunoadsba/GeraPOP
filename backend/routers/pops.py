"""CRUD de POPs + validação + fluxo SEV."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.dependencies import pop_as_dict, pop_from_request
from backend.schemas import (
    CheckCodeRequest,
    PopCreateRequest,
    PopListItem,
    ValidationErrorResponse,
)
from gerapop.codigo import encontrar_codigo_duplicado
from gerapop.fluxo import carregar_fluxo, carregar_pop_fluxo
from gerapop.storage import delete_pop, get_pop, list_pops

router = APIRouter(prefix="/api/pops", tags=["pops"])


def _to_list_item(record: dict) -> PopListItem:
    return PopListItem(
        id=record["id"],
        created_at=record["created_at"],
        status=record.get("status", "generated"),
        codigo=record.get("codigo", ""),
        nome_pop=record.get("nome_pop", ""),
        filename=record.get("filename", ""),
    )


@router.get("", response_model=list[PopListItem])
def listar_pops() -> list[PopListItem]:
    """Lista os POPs salvos (mais recente primeiro)."""
    return [_to_list_item(record) for record in list_pops()]


@router.post("/validate", response_model=ValidationErrorResponse)
def validar_pop(payload: PopCreateRequest) -> ValidationErrorResponse:
    """Valida os campos obrigatórios sem salvar nada."""
    pop = pop_from_request(payload)
    return ValidationErrorResponse(errors=[str(error) for error in pop.validate()])


@router.post("/check-code", response_model=PopListItem | None)
def verificar_codigo(payload: CheckCodeRequest) -> PopListItem | None:
    """Verifica unicidade de código; retorna o conflito mais recente ou null."""
    duplicado = encontrar_codigo_duplicado(payload.codigo, list_pops(), set(payload.allowed_ids))
    if duplicado is None:
        return None
    return _to_list_item(duplicado)


@router.get("/fluxo", response_model=dict | None)
def listar_fluxo() -> dict | None:
    """Retorna os dados do fluxo SEV (nós + links)."""
    return carregar_fluxo()


@router.get("/fluxo/{pop_ref}", response_model=dict | None)
def obter_pop_fluxo(pop_ref: str) -> dict | None:
    """Retorna o POP vinculado a uma etapa do fluxo."""
    pop = carregar_pop_fluxo(pop_ref)
    if pop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POP não encontrado")
    return pop_as_dict(pop)


@router.get("/{pop_id}", response_model=dict)
def obter_pop(pop_id: str) -> dict:
    """Retorna os dados de um POP salvo."""
    pop = get_pop(pop_id)
    if pop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POP não encontrado")
    return pop_as_dict(pop)


@router.delete("/{pop_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_pop(pop_id: str) -> None:
    """Exclui um POP salvo de forma permanente."""
    try:
        if not delete_pop(pop_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POP não encontrado")
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
