"""Estado da sessão Streamlit: formulário, geração e rascunho persistente.

Responsabilidades:
- inicializar e manipular as listas dinâmicas do formulário;
- guardar o POP/docx gerados na sessão corrente;
- preencher/limpar o formulário (modelo, edição, novo POP);
- persistir e restaurar o rascunho entre sessões.
"""

from __future__ import annotations

import io
from datetime import date, datetime
from typing import Any

import streamlit as st

from gerapop.constants import DATE_FORMAT, DEFAULT_VERSAO, SessionKey
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
from gerapop.session_codigo import get_loaded_from, set_loaded_from
from gerapop.storage import DRAFT_FILENAME, get_draft, get_storage_dir, list_pops, save_draft

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


def preparar_novo_pop(nome_pop: str, objetivo: str) -> None:
    """Limpa o formulário e pré-preenche a partir de uma etapa do fluxo.

    Descarta o rascunho/generação atuais para que o novo POP comece zerado
    (o rascunho é re-salvo na próxima execução do formulário).
    """
    clear_generated()
    st.session_state.pop(SessionKey.LOADED_FROM_ID, None)
    st.session_state[SessionKey.NOME_POP] = nome_pop
    st.session_state[SessionKey.CODIGO] = ""
    st.session_state[SessionKey.VERSAO] = DEFAULT_VERSAO
    st.session_state[SessionKey.DATA] = date.today().strftime(DATE_FORMAT)
    st.session_state[SessionKey.AREA] = ""
    st.session_state[SessionKey.AVISO] = ""
    st.session_state[SessionKey.OBJETIVO] = objetivo
    st.session_state[SessionKey.ESCOPO] = ""
    st.session_state[SessionKey.CONSULTA] = ""
    st.session_state[SessionKey.DEFINICOES] = [default_definicao()]
    st.session_state[SessionKey.SECOES] = [default_secao()]
    st.session_state[SessionKey.REGRAS] = [""]
    st.session_state[SessionKey.REVISOES] = [default_revisao()]


_WIDGET_KEY_PREFIXES = (
    "termo_",
    "def_",
    "sec_titulo_",
    "passo_",
    "campo_",
    "campodesc_",
    "regra_",
    "rev",
)


def reset_widgets_formulario() -> None:
    """Remove os estados de widgets do formulário (usado ao carregar/simular).

    Permite que os campos sejam recriados adotando os novos valores na
    próxima renderização, em vez de manter valores antigos das sessões.
    """
    for key in FORM_SCALAR_KEYS + FORM_LIST_KEYS:
        st.session_state.pop(key, None)
    for chave in list(st.session_state):
        if chave.startswith(_WIDGET_KEY_PREFIXES):
            st.session_state.pop(chave, None)
    clear_generated()
    st.session_state.pop(SessionKey.LOADED_FROM_ID, None)


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


def get_draft_saved_at() -> str | None:
    """Horário (HH:MM:SS) do último salvamento automático; None se nunca salvo."""
    try:
        mtime = (get_storage_dir() / DRAFT_FILENAME).stat().st_mtime
    except OSError:
        return None
    return datetime.fromtimestamp(mtime).strftime("%H:%M:%S")


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
