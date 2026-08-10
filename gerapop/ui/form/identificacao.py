"""Seção de identificação do formulário."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import streamlit as st

from gerapop.constants import DATE_FORMAT, DEFAULT_VERSAO, SessionKey
from gerapop.ui.form.widgets import _flag_help


@dataclass(slots=True)
class IdentificacaoFields:
    nome_pop: str
    codigo: str
    versao: str
    data: str
    area: str
    aviso: str


def render_identificacao() -> IdentificacaoFields:
    st.header("Identificação")
    col1, col2 = st.columns(2)

    if SessionKey.VERSAO not in st.session_state:
        st.session_state[SessionKey.VERSAO] = DEFAULT_VERSAO
    if SessionKey.DATA not in st.session_state:
        st.session_state[SessionKey.DATA] = date.today().strftime(DATE_FORMAT)

    with col1:
        nome_pop = st.text_input(
            "Nome do POP *",
            placeholder="Registro de Manobras no Sistema TOS – OpenPort",
            key=SessionKey.NOME_POP,
            help=_flag_help(
                True, "Nome completo do procedimento — ex: Manobra de Atracação de Navio"
            ),
        )
        codigo = st.text_input(
            "Código *",
            placeholder="POP-OPE-XXX",
            key=SessionKey.CODIGO,
            help=_flag_help(True, "Código único do POP — ex: POP-MAN-001"),
        )
        versao = st.text_input(
            "Versão",
            key=SessionKey.VERSAO,
            help=_flag_help(False, "Número da versão — ex: 01, 02"),
        )

    with col2:
        area = st.text_input(
            "Área *",
            placeholder="Operações Portuárias",
            key=SessionKey.AREA,
            help=_flag_help(True, "Setor responsável — ex: Operações Portuárias"),
        )
        data_pop = st.text_input(
            "Data",
            key=SessionKey.DATA,
            help=_flag_help(False, "Data de emissão — usa a data de hoje"),
        )

    aviso = st.text_input(
        "Aviso / Atenção (opcional)",
        placeholder="Ex: Este POP não contempla...",
        key=SessionKey.AVISO,
        help=_flag_help(False, "Alerta importante — ex: Somente com prático credenciado a bordo"),
    )

    return IdentificacaoFields(
        nome_pop=nome_pop,
        codigo=codigo,
        versao=versao,
        data=data_pop,
        area=area,
        aviso=aviso,
    )
