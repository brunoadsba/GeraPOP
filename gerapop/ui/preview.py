"""Pré-visualização em modo leitura de um POP.

Abre um POP (do fluxo ou salvo) em uma tela formatada como documento,
com botões de voltar, editar e baixar .docx/.pdf. O estado é mantido em
`st.session_state[SessionKey.PREVIEW]` como `{"tipo", "ref"}`.
"""

from __future__ import annotations

import html
from collections.abc import Callable

import streamlit as st

from gerapop.constants import DOCX_MIME, PDF_MIME, SessionKey
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf


def abrir_preview(tipo: str, ref: str) -> None:
    """Registra o POP a ser visualizado (tipo: "fluxo" | "salvo")."""
    st.session_state[SessionKey.PREVIEW] = {"tipo": tipo, "ref": ref}


def fechar_preview() -> None:
    st.session_state.pop(SessionKey.PREVIEW, None)


def preview_ativa() -> bool:
    return SessionKey.PREVIEW in st.session_state


def get_preview_estado() -> dict | None:
    estado = st.session_state.get(SessionKey.PREVIEW)
    return estado if isinstance(estado, dict) else None


def _tabela(linhas: list[tuple[str, str]]) -> str:
    """Tabela HTML simples (2 colunas) com as linhas fornecidas."""
    if not linhas:
        return ""
    corpo = "".join(
        f"<tr><td>{html.escape(str(chave))}</td>" f"<td>{html.escape(str(valor))}</td></tr>"
        for chave, valor in linhas
    )
    return '<table class="pop-preview-table"><tbody>' f"{corpo}</tbody></table>"


def _secao(titulo: str) -> None:
    st.markdown(
        f"<div class='pop-preview-eyebrow'>{html.escape(titulo)}</div>",
        unsafe_allow_html=True,
    )


def render_preview(pop: PopData, on_editar: Callable[[], None] | None = None) -> None:
    """Renderiza o POP em modo leitura, formatado como documento."""
    col_voltar, col_acoes = st.columns([1, 2])
    col_voltar.button(
        "← Voltar ao painel",
        key="preview_voltar",
        on_click=fechar_preview,
    )
    with col_acoes:
        col_docx, col_pdf = st.columns(2)
        col_docx.download_button(
            "Baixar .docx",
            data=gerar_docx(pop),
            file_name=pop.output_filename(),
            mime=DOCX_MIME,
            key="preview_docx",
        )
        col_pdf.download_button(
            "Baixar .pdf",
            data=gerar_pdf(pop),
            file_name=pop.output_filename().removesuffix(".docx") + ".pdf",
            mime=PDF_MIME,
            key="preview_pdf",
        )

    st.markdown(
        "<div class='pop-preview-hero'>"
        f"<h1>{html.escape(pop.nome_pop)}</h1>"
        f"<div class='pop-preview-chips'>"
        f"<span class='pop-preview-chip'>{html.escape(pop.codigo)}</span>"
        f"<span class='pop-preview-chip'>v{html.escape(pop.versao)}</span>"
        f"<span class='pop-preview-chip'>{html.escape(pop.data)}</span>"
        f"<span class='pop-preview-chip'>{html.escape(pop.area)}</span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    if pop.aviso:
        st.markdown(
            f"<div class='pop-preview-aviso'>{html.escape(pop.aviso)}</div>",
            unsafe_allow_html=True,
        )

    if pop.objetivo:
        _secao("Objetivo")
        st.write(pop.objetivo)

    if pop.escopo:
        _secao("Escopo e Pré-condições")
        st.write(pop.escopo)

    if pop.definicoes:
        _secao("Definições")
        linhas = [
            (item["termo"], item["definicao"]) for item in pop.definicoes if item.get("termo")
        ]
        if linhas:
            st.markdown(_tabela(linhas), unsafe_allow_html=True)

    if pop.secoes:
        _secao("Procedimento")
        for indice, secao in enumerate(pop.secoes, start=1):
            if not secao.get("titulo"):
                continue
            st.markdown(
                f"<h3 class='pop-preview-h3'>{indice}. "
                f"{html.escape(str(secao['titulo']))}</h3>",
                unsafe_allow_html=True,
            )
            passos = [p for p in secao.get("passos", []) if p]
            for passo in passos:
                st.markdown(
                    f"<div class='pop-preview-passo'>{html.escape(passo)}</div>",
                    unsafe_allow_html=True,
                )
            campos = [
                (campo["campo"], campo["descricao"])
                for campo in secao.get("campos", [])
                if campo.get("campo")
            ]
            if campos:
                st.caption("Campos de registro:")
                st.markdown(_tabela(campos), unsafe_allow_html=True)

    if pop.regras:
        _secao("Regras e Restrições")
        for regra in pop.regras:
            if regra:
                st.markdown(
                    f"<div class='pop-preview-regra'>• {html.escape(regra)}</div>",
                    unsafe_allow_html=True,
                )

    if pop.consulta:
        _secao("Consulta e Relatórios")
        st.write(pop.consulta)

    if pop.revisoes:
        _secao("Histórico de Revisões")
        linhas = [
            (item["revisao"], f"{item.get('data', '')} — {item.get('descricao', '')}")
            for item in pop.revisoes
            if item.get("revisao")
        ]
        if linhas:
            st.markdown(_tabela(linhas), unsafe_allow_html=True)

    if on_editar is not None:
        st.button(
            "Editar este POP",
            key="preview_editar",
            on_click=on_editar,
        )
