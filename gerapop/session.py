from __future__ import annotations

from typing import Any

import streamlit as st

from gerapop.models import Definicao, Revisao, Secao, default_revisao


def init_state() -> None:
    defaults: dict[str, Any] = {
        "definicoes": [{"termo": "", "definicao": ""}],
        "secoes": [{"titulo": "", "passos": [""]}],
        "regras": [""],
        "revisoes": [default_revisao()],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_item(key: str, template: Any) -> None:
    st.session_state[key].append(template)


def remove_item(key: str, idx: int) -> None:
    if len(st.session_state[key]) > 1:
        st.session_state[key].pop(idx)


def add_passo(sec_idx: int) -> None:
    st.session_state["secoes"][sec_idx]["passos"].append("")


def remove_passo(sec_idx: int, passo_idx: int) -> None:
    passos: list[str] = st.session_state["secoes"][sec_idx]["passos"]
    if len(passos) > 1:
        passos.pop(passo_idx)


def get_definicoes() -> list[Definicao]:
    return st.session_state["definicoes"]


def get_secoes() -> list[Secao]:
    return st.session_state["secoes"]


def get_regras() -> list[str]:
    return st.session_state["regras"]


def get_revisoes() -> list[Revisao]:
    return st.session_state["revisoes"]
