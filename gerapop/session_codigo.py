"""Validação de unicidade de código do POP.

Agrupa a regra de código duplicado (função pura + verificação contra o
histórico) e o estado de "registro carregado" que a regra usa como
permissão de edição.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.storage import list_pops


def set_loaded_from(pop_id: str) -> None:
    """Registra o registro que o formulário atual representa (origem de edição)."""
    st.session_state[SessionKey.LOADED_FROM_ID] = pop_id


def get_loaded_from() -> str | None:
    return st.session_state.get(SessionKey.LOADED_FROM_ID)


def encontrar_codigo_duplicado(
    codigo: str,
    records: list[dict[str, Any]],
    ids_permitidos: set[str],
) -> dict[str, Any] | None:
    """Retorna o registro mais recente com o mesmo código fora da permissão.

    Espera a lista ordenada por data de criação desc (como `list_pops`
    entrega), de modo que o primeiro conflito é o registro mais recente.
    Código vazio nunca é considerado duplicado.
    """
    if not codigo:
        return None
    for record in records:
        if record["codigo"] == codigo and record["id"] not in ids_permitidos:
            return record
    return None


def verificar_codigo_duplicado(codigo: str) -> dict[str, Any] | None:
    """Verifica se o código do formulário conflita com o histórico salvo.

    São permitidos: o registro carregado via "Carregar para editar"
    (LOADED_FROM_ID) e o registro salvo na geração atual (SAVED_POP_ID).
    Qualquer outro registro com o mesmo código bloqueia a geração.
    """
    ids_permitidos = {
        pop_id
        for pop_id in (get_loaded_from(), st.session_state.get(SessionKey.SAVED_POP_ID))
        if pop_id
    }
    return encontrar_codigo_duplicado(codigo, list_pops(), ids_permitidos)
