"""Exclusão de POPs salvos — confirmação em 2 cliques compartilhada (histórico e home)."""

from __future__ import annotations

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.session_codigo import get_loaded_from
from gerapop.storage import delete_pop

CONFIRM_EXCLUIR_KEY = "historico_excluir_confirm"


def limpar_estado_orfao(pop_id: str) -> None:
    """Remove referências de sessão a um POP excluído (gerado/edição/preview)."""
    if st.session_state.get(SessionKey.SAVED_POP_ID) == pop_id:
        st.session_state.pop(SessionKey.SAVED_POP_ID, None)
    if get_loaded_from() == pop_id:
        st.session_state.pop(SessionKey.LOADED_FROM_ID, None)
    preview = st.session_state.get(SessionKey.PREVIEW)
    if isinstance(preview, dict) and preview.get("ref") == pop_id:
        st.session_state.pop(SessionKey.PREVIEW, None)


def confirmar_exclusao(record: dict) -> None:
    st.warning(
        f"Excluir permanentemente **{record['nome_pop']}** "
        f"({record['codigo'] or 'sem código'})? Essa ação não pode ser desfeita."
    )
    col_sim, col_nao = st.columns(2)
    if col_sim.button("Sim, excluir", type="primary"):
        if delete_pop(record["id"]):
            limpar_estado_orfao(record["id"])
        st.session_state.pop(CONFIRM_EXCLUIR_KEY, None)
        st.rerun()
    if col_nao.button("Cancelar"):
        st.session_state.pop(CONFIRM_EXCLUIR_KEY, None)
        st.rerun()
