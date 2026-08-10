"""Orquestração da interface Streamlit."""

import io
from collections import Counter
from datetime import datetime

import streamlit as st

from gerapop.constants import DOCX_MIME, PDF_MIME, SessionKey
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf
from gerapop.session_codigo import set_loaded_from
from gerapop.session_draft import (
    clear_generated,
    get_definicoes,
    get_generated_docx,
    get_generated_pop,
    get_regras,
    get_revisoes,
    get_secoes,
    init_state,
    preencher_formulario,
    reset_widgets_formulario,
    restaurar_rascunho,
    salvar_rascunho,
    set_generated_docx,
)
from gerapop.storage import (
    gerar_backup_zip,
    get_docx_bytes,
    get_pop,
    list_pops,
    save_pop,
)
from gerapop.ui import theme
from gerapop.ui.form import (
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
from gerapop.ui.home import (
    MODELO_POP_REF,
    PAGINA_FORM,
    PAGINA_HOME,
    carregar_pop_fluxo,
    render_home,
)
from gerapop.ui.simulacao import render_simulacao


def configure_page() -> None:
    st.set_page_config(page_title="GeraPOP - CODEBA", page_icon="📋", layout="centered")


def _carregar_modelo() -> None:
    pop = carregar_pop_fluxo(MODELO_POP_REF)
    if pop is None:
        return
    reset_widgets_formulario()
    preencher_formulario(pop)


def _render_ajuda_modelo() -> None:
    modelo = carregar_pop_fluxo(MODELO_POP_REF)
    if modelo is None:
        return
    col_texto, col_btn = st.columns([3, 1])
    col_texto.caption(
        f"**Modelo de referência:** {modelo.nome_pop} ({modelo.codigo}) — "
        "exemplo completo de POP preenchido para consulta."
    )
    col_btn.button("Carregar modelo", key="modelo_btn", on_click=_carregar_modelo)


def render_form() -> None:
    render_header()
    _render_ajuda_modelo()
    render_simulacao()

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
    col_docx, col_pdf = st.columns(2)
    col_docx.download_button(
        "Baixar POP (.docx)",
        data=docx,
        file_name=pop.output_filename(),
        mime=DOCX_MIME,
        type="primary",
    )
    col_pdf.download_button(
        "Baixar POP (.pdf)",
        data=gerar_pdf(pop),
        file_name=pop.output_filename().removesuffix(".docx") + ".pdf",
        mime=PDF_MIME,
    )


def _historico_label(record: dict, contagem_codigos: Counter[str]) -> str:
    """Rótulo do selectbox do histórico, com marca de código repetido."""
    codigo = record["codigo"] or "POP"
    label = f"{record['created_at'][:19]} — {codigo} — {record['nome_pop'][:40]}"
    if contagem_codigos[record["codigo"]] > 1:
        label += f" ⚠ ({contagem_codigos[record['codigo']]})"
    return label


def _ver_pop_salvo(pop_id: str) -> None:
    """Abre a preview do POP salvo e navega para a home."""
    st.session_state[SessionKey.PREVIEW] = {"tipo": "salvo", "ref": pop_id}
    st.session_state[SessionKey.PAGE] = PAGINA_HOME


def render_historico() -> None:
    st.divider()
    with st.expander("Histórico de POPs gerados"):
        records = list_pops()
        if not records:
            st.caption("Nenhum POP salvo ainda. Gere um POP para vê-lo aqui.")
            return
        contagem_codigos = Counter(record["codigo"] for record in records)
        labels = {record["id"]: _historico_label(record, contagem_codigos) for record in records}
        selected = st.selectbox(
            "POP salvo",
            [record["id"] for record in records],
            format_func=lambda pop_id: labels[pop_id],
        )
        col_download, col_load = st.columns([2, 2])
        docx_bytes = get_docx_bytes(selected)
        record = next(r for r in records if r["id"] == selected)
        if docx_bytes is not None:
            col_docx, col_pdf = col_download.columns(2)
            col_docx.download_button(
                "Baixar .docx",
                data=docx_bytes,
                file_name=record["filename"],
                mime=DOCX_MIME,
            )
            pop = get_pop(selected)
            if pop is not None:
                col_pdf.download_button(
                    "Baixar .pdf",
                    data=gerar_pdf(pop),
                    file_name=record["filename"].removesuffix(".docx") + ".pdf",
                    mime=PDF_MIME,
                )
        col_ver, col_editar = col_load.columns(2)
        col_ver.button(
            "Visualizar",
            key="historico_ver",
            on_click=_ver_pop_salvo,
            args=(selected,),
        )
        if col_editar.button("Carregar para editar"):
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


def _render_navegacao() -> str:
    return st.sidebar.radio("Navegação", (PAGINA_HOME, PAGINA_FORM), key=SessionKey.PAGE)


def run() -> None:
    configure_page()
    theme.init_theme()
    pagina = _render_navegacao()
    theme.render_theme_toggle()
    if pagina == PAGINA_HOME:
        render_home()
        return
    restaurar_rascunho()
    init_state()
    render_form()
    render_download()
    render_historico()
    salvar_rascunho()
