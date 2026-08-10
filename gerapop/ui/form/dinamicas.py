"""Seções dinâmicas do formulário (listas com adicionar/remover)."""

from __future__ import annotations

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.models import default_definicao, default_secao, empty_revisao
from gerapop.session_draft import (
    add_campo,
    add_item,
    add_passo,
    get_definicoes,
    get_regras,
    get_revisoes,
    get_secoes,
    remove_at,
    remove_campo,
    remove_passo,
)
from gerapop.ui.form.widgets import _flag


def render_definicoes() -> None:
    st.header("Definições")
    _flag(
        True,
        "Termos usados no POP e seus significados — ex: Prático → "
        "profissional que conduz a manobra",
    )
    for index, item in enumerate(get_definicoes()):
        col_termo, col_def, col_action = st.columns([2, 4, 1])
        item["termo"] = col_termo.text_input(
            "Termo",
            value=item["termo"],
            key=f"termo_{index}",
            label_visibility="collapsed",
            placeholder="Termo",
        )
        item["definicao"] = col_def.text_input(
            "Definição",
            value=item["definicao"],
            key=f"def_{index}",
            label_visibility="collapsed",
            placeholder="Definição",
        )
        if len(get_definicoes()) > 1 and col_action.button("Remover", key=f"rm_def_{index}"):
            remove_at(SessionKey.DEFINICOES, index)
            st.rerun()

    st.button(
        "+ Adicionar termo",
        on_click=add_item,
        args=(SessionKey.DEFINICOES, default_definicao()),
    )


def render_procedimento() -> None:
    st.header("Procedimento")
    for secao_index, secao in enumerate(get_secoes()):
        st.subheader(f"Seção {secao_index + 1}")
        _flag(True, "Título da etapa — ex: Preparação da manobra")
        secao["titulo"] = st.text_input(
            "Título da seção",
            value=secao["titulo"],
            key=f"sec_titulo_{secao_index}",
            placeholder="Ex: Procedimento – Atracação",
        )

        _flag(True, "Ações na ordem em que acontecem — ex: Confirmar o horário de chegada (ETA)")
        for passo_index, passo in enumerate(secao["passos"]):
            col_passo, col_action = st.columns([6, 1])
            secao["passos"][passo_index] = col_passo.text_input(
                f"Passo {passo_index + 1}",
                value=passo,
                key=f"passo_{secao_index}_{passo_index}",
                label_visibility="collapsed",
                placeholder=f"Passo {passo_index + 1}",
            )
            if len(secao["passos"]) > 1 and col_action.button(
                "Remover", key=f"rm_passo_{secao_index}_{passo_index}"
            ):
                remove_passo(secao_index, passo_index)
                st.rerun()

        st.button(
            "+ Adicionar passo",
            key=f"add_passo_{secao_index}",
            on_click=add_passo,
            args=(secao_index,),
        )

        _flag(
            False,
            "Campos de registro da etapa — ex: Berço → número do berço designado",
        )
        campos = secao.setdefault("campos", [])
        for campo_index, campo in enumerate(campos):
            col_campo, col_desc, col_action = st.columns([2, 4, 1])
            campo["campo"] = col_campo.text_input(
                "Campo",
                value=campo["campo"],
                key=f"campo_{secao_index}_{campo_index}",
                label_visibility="collapsed",
                placeholder="Campo",
            )
            campo["descricao"] = col_desc.text_input(
                "Descrição",
                value=campo["descricao"],
                key=f"campodesc_{secao_index}_{campo_index}",
                label_visibility="collapsed",
                placeholder="Descrição / Instruções",
            )
            if len(campos) > 1 and col_action.button(
                "Remover", key=f"rm_campo_{secao_index}_{campo_index}"
            ):
                remove_campo(secao_index, campo_index)
                st.rerun()

        st.button(
            "+ Adicionar campo",
            key=f"add_campo_{secao_index}",
            on_click=add_campo,
            args=(secao_index,),
        )

        if len(get_secoes()) > 1 and st.button("Remover seção", key=f"rm_sec_{secao_index}"):
            remove_at(SessionKey.SECOES, secao_index)
            st.rerun()

        st.divider()

    st.button(
        "+ Adicionar seção",
        on_click=add_item,
        args=(SessionKey.SECOES, default_secao()),
    )


def render_regras() -> None:
    st.header("Regras e Restrições")
    _flag(False, "Regras que não podem ser quebradas — ex: Não iniciar sem prático a bordo")
    regras = get_regras()
    for index, regra in enumerate(regras):
        col_regra, col_action = st.columns([6, 1])
        regras[index] = col_regra.text_input(
            "Regra",
            value=regra,
            key=f"regra_{index}",
            label_visibility="collapsed",
            placeholder="Regra",
        )
        if len(get_regras()) > 1 and col_action.button("Remover", key=f"rm_regra_{index}"):
            remove_at(SessionKey.REGRAS, index)
            st.rerun()

    st.button(
        "+ Adicionar regra",
        on_click=add_item,
        args=(SessionKey.REGRAS, ""),
    )


def render_revisoes() -> None:
    st.header("Histórico de Revisões")
    _flag(
        False,
        "Versões anteriores do POP — ex: 02 → 15/03/2026 → Inclusão dos campos obrigatórios",
    )
    for index, revisao in enumerate(get_revisoes()):
        col_rev, col_data, col_desc, col_resp, col_action = st.columns([1, 1.5, 4, 2, 1])
        revisao["revisao"] = col_rev.text_input(
            "Rev.",
            value=revisao["revisao"],
            key=f"rev_{index}",
            label_visibility="collapsed",
        )
        revisao["data"] = col_data.text_input(
            "Data",
            value=revisao["data"],
            key=f"revdata_{index}",
            label_visibility="collapsed",
        )
        revisao["descricao"] = col_desc.text_input(
            "Descrição",
            value=revisao["descricao"],
            key=f"revdesc_{index}",
            label_visibility="collapsed",
            placeholder="Descrição",
        )
        revisao["responsavel"] = col_resp.text_input(
            "Responsável",
            value=revisao["responsavel"],
            key=f"revresp_{index}",
            label_visibility="collapsed",
            placeholder="Responsável",
        )
        if len(get_revisoes()) > 1 and col_action.button("Remover", key=f"rm_rev_{index}"):
            remove_at(SessionKey.REVISOES, index)
            st.rerun()

    st.button(
        "+ Adicionar revisão",
        on_click=add_item,
        args=(SessionKey.REVISOES, empty_revisao()),
    )
