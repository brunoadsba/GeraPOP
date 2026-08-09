from __future__ import annotations

import io
from typing import Any

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.models import (
    Definicao,
    Revisao,
    Secao,
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
