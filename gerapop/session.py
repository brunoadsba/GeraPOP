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
    empty_revisao,
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


def templates() -> dict[str, Any]:
    return {
        "definicao": default_definicao(),
        "secao": default_secao(),
        "regra": "",
        "revisao": empty_revisao(),
    }
