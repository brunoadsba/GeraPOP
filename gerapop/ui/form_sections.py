"""Seções do formulário POP."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date

import streamlit as st

from gerapop.constants import DATE_FORMAT, DEFAULT_VERSAO, SessionKey
from gerapop.models import PopData
from gerapop.session import (
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
    set_generated_pop,
    templates,
    verificar_codigo_duplicado,
)


@dataclass(slots=True)
class IdentificacaoFields:
    nome_pop: str
    codigo: str
    versao: str
    data: str
    area: str
    aviso: str


@dataclass(slots=True)
class ConteudoFields:
    objetivo: str
    escopo: str
    consulta: str


def render_header() -> None:
    st.title("GeraPOP — CODEBA")
    st.caption("Preencha os campos e gere o documento POP formatado (.docx).")


def render_identificacao() -> IdentificacaoFields:
    st.header("Identificação")
    col1, col2 = st.columns(2)

    with col1:
        nome_pop = st.text_input(
            "Nome do POP *",
            placeholder="Registro de Manobras no Sistema TOS – OpenPort",
            key=SessionKey.NOME_POP,
        )
        codigo = st.text_input("Código *", placeholder="POP-OPE-XXX", key=SessionKey.CODIGO)
        versao = st.text_input("Versão", value=DEFAULT_VERSAO, key=SessionKey.VERSAO)

    with col2:
        area = st.text_input("Área *", placeholder="Operações Portuárias", key=SessionKey.AREA)
        data_pop = st.text_input(
            "Data",
            value=date.today().strftime(DATE_FORMAT),
            key=SessionKey.DATA,
        )

    aviso = st.text_input(
        "Aviso / Atenção (opcional)",
        placeholder="Ex: Este POP não contempla...",
        key=SessionKey.AVISO,
    )

    return IdentificacaoFields(nome_pop, codigo, versao, data_pop, area, aviso)


def render_objetivo_escopo() -> tuple[str, str]:
    st.header("Objetivo")
    objetivo = st.text_area(
        "Descreva o objetivo do procedimento *", height=100, key=SessionKey.OBJETIVO
    )

    st.header("Escopo e Pré-condições")
    escopo = st.text_area("A quem se aplica / condições prévias", height=100, key=SessionKey.ESCOPO)

    return objetivo, escopo


def render_definicoes() -> None:
    st.header("Definições")
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
        args=(SessionKey.DEFINICOES, templates()["definicao"]),
    )


def render_procedimento() -> None:
    st.header("Procedimento")
    for secao_index, secao in enumerate(get_secoes()):
        st.subheader(f"Seção {secao_index + 1}")
        secao["titulo"] = st.text_input(
            "Título da seção",
            value=secao["titulo"],
            key=f"sec_titulo_{secao_index}",
            placeholder="Ex: Procedimento – Atracação",
        )

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
        args=(SessionKey.SECOES, templates()["secao"]),
    )


def render_regras() -> None:
    st.header("Regras e Restrições")
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
        args=(SessionKey.REGRAS, templates()["regra"]),
    )


def render_consulta() -> str:
    st.header("Consulta e Relatórios")
    return st.text_area(
        "Caminho / menu para consulta (opcional)", height=70, key=SessionKey.CONSULTA
    )


def render_revisoes() -> None:
    st.header("Histórico de Revisões")
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
        args=(SessionKey.REVISOES, templates()["revisao"]),
    )


def build_pop(identificacao: IdentificacaoFields, conteudo: ConteudoFields) -> PopData:
    return PopData.from_form(
        nome_pop=identificacao.nome_pop,
        codigo=identificacao.codigo,
        versao=identificacao.versao,
        data=identificacao.data,
        area=identificacao.area,
        aviso=identificacao.aviso,
        objetivo=conteudo.objetivo,
        escopo=conteudo.escopo,
        definicoes=get_definicoes(),
        secoes=get_secoes(),
        regras=get_regras(),
        consulta=conteudo.consulta,
        revisoes=get_revisoes(),
    )


def try_generate(identificacao: IdentificacaoFields, conteudo: ConteudoFields) -> None:
    pop = build_pop(identificacao, conteudo)
    errors = pop.validate()
    if errors:
        for error in errors:
            st.error(error)
        return

    duplicado = verificar_codigo_duplicado(pop.codigo)
    if duplicado is not None:
        st.error(
            f"O código {pop.codigo} já é usado pelo POP '{duplicado['nome_pop']}' "
            f"(criado em {duplicado['created_at'][:16]}). Use um código diferente "
            "ou carregue o POP existente no histórico para editá-lo."
        )
        return

    set_generated_pop(deepcopy(pop))
    st.rerun()
