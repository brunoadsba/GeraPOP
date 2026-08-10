"""Botões de download de documentos POP (.docx / .pdf) reutilizáveis.

Centraliza o par de botões de download que aparece no preview, no dashboard
e no formulário — nome de arquivo, MIME e derivação do nome do PDF em um só
lugar.
"""

from __future__ import annotations

import io

import streamlit as st

from gerapop.constants import DOCX_MIME, PDF_MIME


def _nome_pdf(nome_docx: str) -> str:
    """Deriva o nome do arquivo .pdf a partir do nome do .docx."""
    return nome_docx.removesuffix(".docx") + ".pdf"


def botao_docx(
    data: bytes | io.BytesIO,
    nome_arquivo: str,
    *,
    key: str | None = None,
    label: str = "Baixar .docx",
    primary: bool = False,
    container=None,
) -> None:
    """Botão de download do .docx (container opcional = st ou coluna)."""
    alvo = container or st
    alvo.download_button(
        label,
        data=data,
        file_name=nome_arquivo,
        mime=DOCX_MIME,
        key=key,
        **({"type": "primary"} if primary else {}),
    )


def botao_pdf(
    data: bytes | io.BytesIO,
    nome_arquivo_docx: str,
    *,
    key: str | None = None,
    label: str = "Baixar .pdf",
    container=None,
) -> None:
    """Botão de download do .pdf (nome derivado do .docx)."""
    alvo = container or st
    alvo.download_button(
        label,
        data=data,
        file_name=_nome_pdf(nome_arquivo_docx),
        mime=PDF_MIME,
        key=key,
    )


def render_downloads(
    data_docx: bytes | io.BytesIO,
    data_pdf: bytes | io.BytesIO,
    nome_arquivo: str,
    *,
    key_docx: str | None = None,
    key_pdf: str | None = None,
    label_docx: str = "Baixar .docx",
    label_pdf: str = "Baixar .pdf",
    docx_primary: bool = False,
) -> None:
    """Par de botões (docx + pdf) lado a lado, com nomes derivados."""
    col_docx, col_pdf = st.columns(2)
    botao_docx(
        data_docx,
        nome_arquivo,
        key=key_docx,
        label=label_docx,
        primary=docx_primary,
        container=col_docx,
    )
    botao_pdf(data_pdf, nome_arquivo, key=key_pdf, label=label_pdf, container=col_pdf)
