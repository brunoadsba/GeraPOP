"""Histórico de POPs salvos — listagem, download, edição e backup."""

from __future__ import annotations

from collections import Counter
from datetime import datetime

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.services.pdf import gerar_pdf
from gerapop.session_codigo import set_loaded_from
from gerapop.session_draft import preencher_formulario
from gerapop.storage import gerar_backup_zip, get_docx_bytes, get_pop, list_pops
from gerapop.ui.downloads import botao_docx, botao_pdf
from gerapop.ui.home import PAGINA_HOME


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
            botao_docx(docx_bytes, record["filename"], container=col_docx)
            pop = get_pop(selected)
            if pop is not None:
                botao_pdf(gerar_pdf(pop), record["filename"], container=col_pdf)
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
