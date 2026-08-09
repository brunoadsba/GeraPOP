"""Orquestração da interface Streamlit."""

import io
import json
from collections import Counter
from datetime import datetime

import streamlit as st

from gerapop.constants import DOCX_MIME, JSON_MIME, SessionKey
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.session import (
    clear_generated,
    get_definicoes,
    get_generated_docx,
    get_generated_pop,
    get_regras,
    get_revisoes,
    get_secoes,
    init_state,
    preencher_formulario,
    restaurar_rascunho,
    salvar_rascunho,
    set_generated_docx,
    set_loaded_from,
)
from gerapop.storage import (
    gerar_backup_zip,
    get_docx_bytes,
    get_pop,
    get_pop_json_bytes,
    list_pops,
    save_pop,
    serialize_pop,
)
from gerapop.ui.form_sections import (
    ConteudoFields,
    IdentificacaoFields,
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

    _sync_generated_state(identificacao, conteudo)


def _form_matches_generated(
    identificacao: IdentificacaoFields,
    conteudo: ConteudoFields,
    pop: PopData,
) -> bool:
    fields_match = (
        identificacao.nome_pop == pop.nome_pop
        and identificacao.codigo == pop.codigo
        and identificacao.versao == pop.versao
        and identificacao.data == pop.data
        and identificacao.area == pop.area
        and identificacao.aviso == pop.aviso
        and conteudo.objetivo == pop.objetivo
        and conteudo.escopo == pop.escopo
        and conteudo.consulta == pop.consulta
    )
    lists_match = (
        get_definicoes() == pop.definicoes
        and get_secoes() == pop.secoes
        and get_regras() == pop.regras
        and get_revisoes() == pop.revisoes
    )
    return fields_match and lists_match


def _sync_generated_state(
    identificacao: IdentificacaoFields,
    conteudo: ConteudoFields,
) -> None:
    pop = get_generated_pop()
    if pop is not None and not _form_matches_generated(identificacao, conteudo, pop):
        clear_generated()


def _salvar_generated(pop: PopData, docx: io.BytesIO) -> None:
    if SessionKey.SAVED_POP_ID in st.session_state:
        return
    pop_id = save_pop(pop, docx.getvalue())
    st.session_state[SessionKey.SAVED_POP_ID] = pop_id
    set_loaded_from(pop_id)


def render_download() -> None:
    pop: PopData | None = get_generated_pop()
    if not pop:
        return

    st.success("POP gerado com sucesso.")
    docx = get_generated_docx()
    if docx is None:
        docx = gerar_docx(pop)
        set_generated_docx(docx)
        _salvar_generated(pop, docx)
    col_docx, col_json = st.columns(2)
    col_docx.download_button(
        "Baixar POP (.docx)",
        data=docx,
        file_name=pop.output_filename(),
        mime=DOCX_MIME,
        type="primary",
    )
    col_json.download_button(
        "Baixar POP (.json)",
        data=json.dumps(serialize_pop(pop), ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=pop.output_filename().removesuffix(".docx") + ".json",
        mime=JSON_MIME,
    )


def _historico_label(record: dict, contagem_codigos: Counter) -> str:
    """Rótulo do selectbox do histórico, com marca de código repetido."""
    codigo = record["codigo"] or "POP"
    label = f"{record['created_at'][:19]} — {codigo} — {record['nome_pop'][:40]}"
    if contagem_codigos[record["codigo"]] > 1:
        label += f" ⚠ ({contagem_codigos[record['codigo']]})"
    return label


def render_historico() -> None:
    st.divider()
    with st.expander("Histórico de POPs gerados"):
        records = list_pops()
        if not records:
            st.caption("Nenhum POP salvo ainda. Gere um POP para vê-lo aqui.")
            return
        contagem_codigos = Counter(record["codigo"] for record in records)
        labels = {
            record["id"]: _historico_label(record, contagem_codigos)
            for record in records
        }
        selected = st.selectbox(
            "POP salvo",
            [record["id"] for record in records],
            format_func=lambda pop_id: labels[pop_id],
        )
        col_download, col_load = st.columns([2, 1])
        docx_bytes = get_docx_bytes(selected)
        json_bytes = get_pop_json_bytes(selected)
        record = next(r for r in records if r["id"] == selected)
        if docx_bytes is not None:
            col_docx, col_json = col_download.columns(2)
            col_docx.download_button(
                "Baixar .docx",
                data=docx_bytes,
                file_name=record["filename"],
                mime=DOCX_MIME,
            )
            if json_bytes is not None:
                col_json.download_button(
                    "Baixar .json",
                    data=json_bytes,
                    file_name=record["filename"].removesuffix(".docx") + ".json",
                    mime=JSON_MIME,
                )
        if col_load.button("Carregar para editar"):
            pop = get_pop(selected)
            if pop is not None:
                set_loaded_from(selected)
                preencher_formulario(pop)
                st.rerun()

        st.divider()
        st.download_button(
            "Baixar backup (.zip)",
            data=gerar_backup_zip(),
            file_name=f"gerapop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
        )


def run() -> None:
    configure_page()
    restaurar_rascunho()
    init_state()
    render_form()
    render_download()
    render_historico()
    salvar_rascunho()
