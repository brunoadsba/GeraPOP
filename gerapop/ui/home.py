"""Tela inicial (home) — painel dashboard do fluxo SEV.

Lê o fluxo em `fluxo-sev/data/fluxo-desembarque.json` e os POPs vinculados
em `fluxo-sev/data/pops/`, apresentando um painel com KPIs, stepper das
etapas e cards de gerados/pendentes.
"""

from __future__ import annotations

import html
import json
from functools import partial
from pathlib import Path

import streamlit as st

from gerapop.constants import DOCX_MIME, PDF_MIME, SessionKey
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf
from gerapop.session_codigo import set_loaded_from
from gerapop.session_draft import (
    preencher_formulario,
    preparar_novo_pop,
    reset_widgets_formulario,
)
from gerapop.ui.preview import (
    fechar_preview,
    get_preview_estado,
    preview_ativa,
    render_preview,
)

PAGINA_HOME = "🏠 Início"
PAGINA_FORM = "📝 Formulário"
MODELO_POP_REF = "pop-desembarque"

FLUXO_DATA_DIR = Path(__file__).resolve().parents[2] / "fluxo-sev" / "data"
FLUXO_FILE = FLUXO_DATA_DIR / "fluxo-desembarque.json"
FLUXO_POPS_DIR = FLUXO_DATA_DIR / "pops"


def carregar_fluxo(path: Path | None = None) -> dict | None:
    """Lê o JSON do fluxo; None quando inexistente ou inválido."""
    try:
        payload = json.loads((path or FLUXO_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def classificar_nos(fluxo: dict) -> tuple[list[dict], list[dict]]:
    """Separa (pendentes, gerados) — nós sem e com pop_ref, por etapa."""
    nos = sorted(fluxo.get("nos", []), key=lambda no: no.get("etapa", 0))
    pendentes = [no for no in nos if not no.get("pop_ref")]
    gerados = [no for no in nos if no.get("pop_ref")]
    return pendentes, gerados


def carregar_pop_fluxo(pop_ref: str) -> PopData | None:
    """Converte o JSON de `fluxo-sev/data/pops/<pop_ref>.json` em PopData."""
    path = FLUXO_POPS_DIR / f"{pop_ref}.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    try:
        return PopData(**payload["pop"])
    except (KeyError, TypeError):
        return None


def _ir_para_formulario() -> None:
    """Callback de navegação — roda antes do re-render, então pode setar o radio."""
    st.session_state[SessionKey.PAGE] = PAGINA_FORM


def _criar_pop_e_ir(nome_pop: str, objetivo: str) -> None:
    preparar_novo_pop(nome_pop, objetivo)
    _ir_para_formulario()


def _editar_pop_e_ir(pop: PopData) -> None:
    preencher_formulario(pop)
    _ir_para_formulario()


def _render_hero(fluxo: dict, total: int, gerados: int, pendentes: int) -> None:
    concluido = round(gerados / total * 100) if total else 0
    kpis = (
        ("📋", str(total), "Etapas"),
        ("📄", str(gerados), "POPs gerados"),
        ("⏳", str(pendentes), "Pendentes"),
        ("✅", f"{concluido}%", "Concluído"),
    )
    kpi_html = "".join(
        f'<div class="pop-dash-kpi"><div class="pop-dash-kpi-icon">{icone}</div>'
        f'<div class="pop-dash-kpi-value">{valor}</div>'
        f'<div class="pop-dash-kpi-label">{rotulo}</div></div>'
        for icone, valor, rotulo in kpis
    )
    st.markdown(
        f"""
        <div class="pop-dash-hero">
          <span class="pop-dash-badge">Fluxo SEV</span>
          <h1>{html.escape(str(fluxo.get('titulo', 'Fluxo SEV')))}</h1>
          <p>{html.escape(str(fluxo.get('descricao', '')))}</p>
        </div>
        <div class="pop-dash-kpis">{kpi_html}</div>
        """,
        unsafe_allow_html=True,
    )


def _render_stepper(fluxo: dict) -> None:
    nos = sorted(fluxo.get("nos", []), key=lambda no: no.get("etapa", 0))
    if not nos:
        return
    passos_html = []
    viu_pendente = False
    for no in nos:
        done = bool(no.get("pop_ref"))
        if done:
            estado = " done"
        elif not viu_pendente:
            estado = " current"
            viu_pendente = True
        else:
            estado = ""
        rotulo = html.escape(str(no.get("rotulo", "")))
        marcador = "✓" if done else str(no.get("etapa", ""))
        passos_html.append(
            f'<div class="pop-dash-step{estado}" title="{rotulo}">'
            f'<div class="pop-dash-dot">{marcador}</div>'
            f'<div class="pop-dash-step-label">{rotulo}</div></div>'
        )
    st.markdown(
        f'<div class="pop-dash-steps">{"".join(passos_html)}</div>',
        unsafe_allow_html=True,
    )


def _render_gerados(gerados: list[dict]) -> None:
    st.header(f"📄 POPs gerados ({len(gerados)})")
    if not gerados:
        st.caption("Nenhuma etapa do fluxo possui POP vinculado ainda.")
        return
    for i in range(0, len(gerados), 2):
        col_esq, col_dir = st.columns(2)
        for col, no in zip((col_esq, col_dir), gerados[i : i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"**{html.escape(str(no['rotulo']))}**"
                        f"<span class='pop-dash-chip gerado'>etapa {no['etapa']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(no["descricao"])
                    pop_ref = no["pop_ref"]
                    pop = carregar_pop_fluxo(pop_ref)
                    if pop is None:
                        st.warning(
                            f"POP referenciado `{pop_ref}` não encontrado em fluxo-sev/data/pops."
                        )
                        continue
                    if st.button(
                        "Visualizar POP",
                        key=f"ver_{no['id']}",
                        on_click=_abrir_preview_fluxo,
                        args=(pop_ref,),
                    ):
                        pass
                    col_docx, col_pdf, col_editar = st.columns(3)
                    col_docx.download_button(
                        "Baixar .docx",
                        data=gerar_docx(pop),
                        file_name=pop.output_filename(),
                        mime=DOCX_MIME,
                        key=f"docx_{no['id']}",
                    )
                    col_pdf.download_button(
                        "Baixar .pdf",
                        data=gerar_pdf(pop),
                        file_name=pop.output_filename().removesuffix(".docx") + ".pdf",
                        mime=PDF_MIME,
                        key=f"pdf_{no['id']}",
                    )
                    col_editar.button(
                        "Editar POP",
                        key=f"editar_{no['id']}",
                        on_click=_editar_pop_e_ir,
                        args=(pop,),
                    )


def _render_pendentes(pendentes: list[dict]) -> None:
    st.header(f"⏳ POPs pendentes ({len(pendentes)})")
    if not pendentes:
        st.success("Todas as etapas do fluxo já possuem POP.")
        return
    for i in range(0, len(pendentes), 2):
        col_esq, col_dir = st.columns(2)
        for col, no in zip((col_esq, col_dir), pendentes[i : i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(
                        f"**{html.escape(str(no['rotulo']))}**"
                        f"<span class='pop-dash-chip pendente'>etapa {no['etapa']}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(no["descricao"])
                    st.button(
                        "Criar POP",
                        type="primary",
                        key=f"criar_{no['id']}",
                        on_click=_criar_pop_e_ir,
                        args=(no["rotulo"], no["descricao"]),
                    )


def _ver_modelo(pop: PopData) -> None:
    reset_widgets_formulario()
    preencher_formulario(pop)
    _ir_para_formulario()


def _render_modelo() -> None:
    pop = carregar_pop_fluxo(MODELO_POP_REF)
    if pop is None:
        return
    st.header("📌 Modelo de referência")
    with st.container(border=True):
        st.markdown(f"**{html.escape(pop.nome_pop)}** — {html.escape(pop.codigo)} (v{pop.versao})")
        st.caption("Exemplo completo de POP preenchido, validado contra o modelo OpenPort.")
        col_ver, col_docx = st.columns(2)
        col_ver.button(
            "Ver modelo no formulário",
            key="modelo_ver",
            on_click=_ver_modelo,
            args=(pop,),
        )
        col_docx.download_button(
            "Baixar .docx",
            data=gerar_docx(pop),
            file_name=pop.output_filename(),
            mime=DOCX_MIME,
            key="modelo_docx",
        )


def _abrir_preview_fluxo(pop_ref: str) -> None:
    st.session_state[SessionKey.PREVIEW] = {"tipo": "fluxo", "ref": pop_ref}


def _editar_preview_e_ir(pop: PopData, pop_id: str | None = None) -> None:
    """Fecha a preview e abre o POP no formulário (pop_id = registro salvo)."""
    fechar_preview()
    if pop_id is not None:
        from gerapop.session_codigo import set_loaded_from

        set_loaded_from(pop_id)
    _editar_pop_e_ir(pop)


def _render_preview_ativa() -> None:
    """Renderiza o POP em preview (fluxo ou salvo); limpa estado se inválido."""
    estado = get_preview_estado()
    if estado is None:
        return
    if estado.get("tipo") == "salvo":
        from gerapop.storage import get_pop

        pop = get_pop(estado["ref"])
        on_editar = partial(_editar_preview_e_ir, pop, estado["ref"])
    else:
        pop = carregar_pop_fluxo(estado["ref"])
        on_editar = partial(_editar_preview_e_ir, pop)
    if pop is None:
        st.warning(f"POP `{estado['ref']}` não encontrado.")
        fechar_preview()
        return
    render_preview(pop, on_editar=on_editar)


def render_home() -> None:
    if preview_ativa():
        _render_preview_ativa()
        return

    fluxo = carregar_fluxo()
    if fluxo is None:
        st.title(PAGINA_HOME)
        st.warning(
            "Não foi possível carregar o fluxo SEV. "
            f"Esperado em `{FLUXO_FILE}`. "
            "Use o menu '📝 Formulário' para criar um POP avulso."
        )
        return

    pendentes, gerados = classificar_nos(fluxo)
    total = len(pendentes) + len(gerados)

    _render_hero(fluxo, total, len(gerados), len(pendentes))
    _render_stepper(fluxo)
    _render_modelo()
    _render_gerados(gerados)
    _render_pendentes(pendentes)
