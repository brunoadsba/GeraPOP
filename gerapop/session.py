from __future__ import annotations

import io
from typing import Any

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.models import (
    Definicao,
    PopData,
    Revisao,
    Secao,
    default_campo,
    default_definicao,
    default_revisao,
    default_secao,
)
from gerapop.storage import get_draft, list_pops, save_draft

FORM_SCALAR_KEYS = (
    SessionKey.NOME_POP,
    SessionKey.CODIGO,
    SessionKey.VERSAO,
    SessionKey.DATA,
    SessionKey.AREA,
    SessionKey.AVISO,
    SessionKey.OBJETIVO,
    SessionKey.ESCOPO,
    SessionKey.CONSULTA,
)

FORM_LIST_KEYS = (
    SessionKey.DEFINICOES,
    SessionKey.SECOES,
    SessionKey.REGRAS,
    SessionKey.REVISOES,
)


def init_state() -> None:
    defaults: dict[SessionKey, Any] = {
        SessionKey.DEFINICOES: [default_definicao()],
        SessionKey.SECOES: [default_secao()],
        SessionKey.REGRAS: [""],
        SessionKey.REVISOES: [default_revisao()],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_item(key: SessionKey, template: Any) -> None:
    st.session_state[key].append(template)


def remove_at(key: SessionKey, index: int) -> None:
    if len(st.session_state[key]) > 1:
        st.session_state[key].pop(index)


def add_passo(secao_index: int) -> None:
    st.session_state[SessionKey.SECOES][secao_index]["passos"].append("")


def remove_passo(secao_index: int, passo_index: int) -> None:
    passos: list[str] = st.session_state[SessionKey.SECOES][secao_index]["passos"]
    if len(passos) > 1:
        passos.pop(passo_index)


def add_campo(secao_index: int) -> None:
    get_secoes()[secao_index].setdefault("campos", []).append(default_campo())


def remove_campo(secao_index: int, campo_index: int) -> None:
    campos = get_secoes()[secao_index].setdefault("campos", [])
    if len(campos) > 1:
        campos.pop(campo_index)


def get_definicoes() -> list[Definicao]:
    return st.session_state[SessionKey.DEFINICOES]


def get_secoes() -> list[Secao]:
    return st.session_state[SessionKey.SECOES]


def get_regras() -> list[str]:
    return st.session_state[SessionKey.REGRAS]


def get_revisoes() -> list[Revisao]:
    return st.session_state[SessionKey.REVISOES]


def set_generated_pop(pop: Any) -> None:
    st.session_state[SessionKey.GENERATED_POP] = pop


def get_generated_pop() -> Any | None:
    return st.session_state.get(SessionKey.GENERATED_POP)


def clear_generated() -> None:
    st.session_state.pop(SessionKey.GENERATED_POP, None)
    st.session_state.pop(SessionKey.GENERATED_DOCX, None)
    st.session_state.pop(SessionKey.SAVED_POP_ID, None)


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


def preencher_formulario(pop: PopData) -> None:
    st.session_state[SessionKey.NOME_POP] = pop.nome_pop
    st.session_state[SessionKey.CODIGO] = pop.codigo
    st.session_state[SessionKey.VERSAO] = pop.versao
    st.session_state[SessionKey.DATA] = pop.data
    st.session_state[SessionKey.AREA] = pop.area
    st.session_state[SessionKey.AVISO] = pop.aviso
    st.session_state[SessionKey.OBJETIVO] = pop.objetivo
    st.session_state[SessionKey.ESCOPO] = pop.escopo
    st.session_state[SessionKey.CONSULTA] = pop.consulta
    st.session_state[SessionKey.DEFINICOES] = pop.definicoes
    st.session_state[SessionKey.SECOES] = pop.secoes
    st.session_state[SessionKey.REGRAS] = pop.regras
    st.session_state[SessionKey.REVISOES] = pop.revisoes


def set_generated_docx(docx: io.BytesIO) -> None:
    st.session_state[SessionKey.GENERATED_DOCX] = docx


def get_generated_docx() -> io.BytesIO | None:
    return st.session_state.get(SessionKey.GENERATED_DOCX)


def obter_sid() -> str | None:
    """ID da sessão Streamlit atual (None fora de um runtime ativo)."""
    try:
        ctx = st.runtime.scriptrunner.get_script_run_ctx()
    except Exception:
        return None
    return ctx.session_id if ctx is not None else None


def salvar_rascunho() -> None:
    form: dict[str, Any] = {
        str(key): st.session_state.get(key) for key in FORM_SCALAR_KEYS + FORM_LIST_KEYS
    }
    payload: dict[str, Any] = {
        "session_id": obter_sid(),
        "form": form,
        "loaded_from_id": get_loaded_from(),
    }
    if payload != get_draft():
        save_draft(payload)


def restaurar_rascunho() -> None:
    """Restaura o rascunho salvo na primeira execução de cada sessão."""
    if SessionKey.DRAFT_RESTORED in st.session_state:
        return
    st.session_state[SessionKey.DRAFT_RESTORED] = True
    payload = get_draft()
    if payload is None:
        return
    form = payload.get("form", {})
    for key in FORM_SCALAR_KEYS:
        if str(key) in form:
            st.session_state[key] = form[str(key)]
    for key in FORM_LIST_KEYS:
        if str(key) in form:
            st.session_state[key] = form[str(key)]
    loaded_from_id = payload.get("loaded_from_id")
    if loaded_from_id and any(record["id"] == loaded_from_id for record in list_pops()):
        set_loaded_from(loaded_from_id)
