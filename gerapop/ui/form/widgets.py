"""Helpers compartilhados do formulário (badges de flag e cabeçalho)."""

from __future__ import annotations

import streamlit as st


def _flag(obrigatorio: bool, exemplo: str) -> None:
    """Badge obrigatório/opcional + orientação de preenchimento com exemplo."""
    badge = "OBRIGATÓRIO" if obrigatorio else "OPCIONAL"
    cls = "pop-flag-req" if obrigatorio else "pop-flag-opt"
    st.markdown(
        f"<div class='pop-flag-row'><span class='pop-flag {cls}'>{badge}</span>"
        f"<span class='pop-flag-hint'>{exemplo}</span></div>",
        unsafe_allow_html=True,
    )


def _flag_help(obrigatorio: bool, exemplo: str) -> str:
    """Badge sem hint inline; devolve o exemplo para usar como tooltip nativo."""
    badge = "OBRIGATÓRIO" if obrigatorio else "OPCIONAL"
    cls = "pop-flag-req" if obrigatorio else "pop-flag-opt"
    st.markdown(
        f"<div class='pop-flag-row'><span class='pop-flag {cls}'>{badge}</span></div>",
        unsafe_allow_html=True,
    )
    return exemplo


def render_header() -> None:
    st.title("GeraPOP — CODEBA")
    st.caption("Preencha os campos e gere o documento POP formatado (.docx).")
