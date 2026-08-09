"""Orquestração da interface Streamlit."""

import streamlit as st

from gerapop.constants import DOCX_MIME
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.session import get_generated_pop, init_state
from gerapop.ui.form_sections import (
    ConteudoFields,
    render_consulta,
    render_definicoes,
    render_header,
    render_identificacao,
    render_objetivo_escopo,
    render_procedimento,
    render_regras,
    render_revisoes,
    try_generate,
)


def configure_page() -> None:
    st.set_page_config(page_title="GeraPOP - CODEBA", page_icon="📋", layout="centered")


def render_form() -> None:
    render_header()

    identificacao = render_identificacao()
    objetivo, escopo = render_objetivo_escopo()
    render_definicoes()
    render_procedimento()
    render_regras()
    consulta = render_consulta()
    render_revisoes()

    conteudo = ConteudoFields(objetivo=objetivo, escopo=escopo, consulta=consulta)

    st.divider()
    if st.button("Gerar POP (.docx)", type="primary"):
        try_generate(identificacao, conteudo)


def render_download() -> None:
    pop: PopData | None = get_generated_pop()
    if not pop:
        return

    st.success("POP gerado com sucesso.")
    st.download_button(
        "Baixar POP (.docx)",
        data=gerar_docx(pop),
        file_name=pop.output_filename(),
        mime=DOCX_MIME,
        type="primary",
    )


def run() -> None:
    configure_page()
    init_state()
    render_form()
    render_download()
