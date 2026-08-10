"""Seções de conteúdo do formulário e geração do POP."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.models import PopData
from gerapop.session_codigo import verificar_codigo_duplicado
from gerapop.session_draft import (
    get_definicoes,
    get_regras,
    get_revisoes,
    get_secoes,
    set_generated_pop,
)
from gerapop.ui.form.identificacao import IdentificacaoFields
from gerapop.ui.form.widgets import _flag_help


@dataclass(slots=True)
class ConteudoFields:
    objetivo: str
    escopo: str
    consulta: str


def render_objetivo_escopo() -> tuple[str, str]:
    st.header("Objetivo")
    objetivo = st.text_area(
        "Descreva o objetivo do procedimento *",
        height=100,
        key=SessionKey.OBJETIVO,
        help=_flag_help(
            True, "O que o procedimento padroniza — ex: Padronizar a manobra de atracação de navios"
        ),
    )

    st.header("Escopo e Pré-condições")
    escopo = st.text_area(
        "A quem se aplica / condições prévias",
        height=100,
        key=SessionKey.ESCOPO,
        help=_flag_help(
            False,
            "A quem se aplica e condições prévias — ex: Equipe de operações, práticos, rebocadores",
        ),
    )

    return objetivo, escopo


def render_consulta() -> str:
    st.header("Consulta e Relatórios")
    return st.text_area(
        "Caminho / menu para consulta (opcional)",
        height=70,
        key=SessionKey.CONSULTA,
        help=_flag_help(False, "Onde o registro é consultado — ex: Menu > Operações > Manobras"),
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
