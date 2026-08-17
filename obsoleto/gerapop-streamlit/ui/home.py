"""Tela inicial (home) — painel dashboard do fluxo SEV.

Lê o fluxo em `fluxo-sev/data/fluxo-desembarque.json` e os POPs vinculados
em `fluxo-sev/data/pops/`, apresentando um painel com KPIs, stepper das
etapas e cards de gerados/pendentes.
"""

from __future__ import annotations

import html
import json
from collections.abc import Callable
from functools import partial
from pathlib import Path

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf
from gerapop.session_codigo import set_loaded_from
from gerapop.session_draft import (
    preencher_formulario,
    preparar_novo_pop,
    reset_widgets_formulario,
)
from gerapop.storage import get_docx_bytes, get_pop, list_pops
from gerapop.ui.downloads import botao_docx, botao_pdf
from gerapop.ui.exclusao import CONFIRM_EXCLUIR_KEY, confirmar_exclusao
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


def _render_hero(fluxo: dict, total: int, gerados: int, pendentes: int, pops_salvos: int) -> None:
    concluido = round(gerados / total * 100) if total else 0
    kpis = (
        ("📋", str(total), "Etapas"),
        ("📄", str(pops_salvos), "POPs gerados"),
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
          <h1>{html.escape(str(fluxo.get("titulo", "Fluxo SEV")))}</h1>
          <p>{html.escape(str(fluxo.get("descricao", "")))}</p>
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


def _render_grade(nos: list[dict], chip_cls: str, corpo: Callable[[dict], None]) -> None:
    """Renderiza os cards em grade de 2 colunas; `corpo` recebe cada nó.

    Aceita nós do fluxo (rotulo/etapa/descricao) e registros salvos
    (nome_pop/codigo/created_at) — campos ausentes caem nos fallbacks.
    """
    for i in range(0, len(nos), 2):
        col_esq, col_dir = st.columns(2)
        for col, no in zip((col_esq, col_dir), nos[i : i + 2]):
            with col:
                with st.container(border=True):
                    titulo = no.get("rotulo") or no.get("nome_pop", "?")
                    chip = no.get("etapa") or no.get("codigo", "")
                    descricao = no.get("descricao") or no.get("created_at", "")
                    st.markdown(
                        f"**{html.escape(str(titulo))}**"
                        f"<span class='pop-dash-chip {chip_cls}'>"
                        f"{html.escape(str(chip))}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(descricao)
                    corpo(no)


def _corpo_card_gerado(no: dict) -> None:
    pop_ref = no["pop_ref"]
    pop = carregar_pop_fluxo(pop_ref)
    if pop is None:
        st.warning(f"POP referenciado `{pop_ref}` não encontrado em fluxo-sev/data/pops.")
        return
    if st.button(
        "Visualizar POP",
        key=f"ver_{no['id']}",
        on_click=_abrir_preview_fluxo,
        args=(pop_ref,),
    ):
        pass
    col_docx, col_pdf, col_editar = st.columns(3)
    botao_docx(
        gerar_docx(pop),
        pop.output_filename(),
        key=f"docx_{no['id']}",
        container=col_docx,
    )
    botao_pdf(
        gerar_pdf(pop),
        pop.output_filename(),
        key=f"pdf_{no['id']}",
        container=col_pdf,
    )
    col_editar.button(
        "Editar POP",
        key=f"editar_{no['id']}",
        on_click=_editar_pop_e_ir,
        args=(pop,),
    )


def _render_gerados(gerados: list[dict], total_etapas: int) -> None:
    st.header(f"📄 Etapas com POP ({len(gerados)}/{total_etapas})")
    if not gerados:
        st.caption("Nenhuma etapa do fluxo possui POP vinculado ainda.")
        return
    _render_grade(gerados, "gerado", _corpo_card_gerado)


def _corpo_card_pendente(no: dict) -> None:
    st.button(
        "Criar POP",
        type="primary",
        key=f"criar_{no['id']}",
        on_click=_criar_pop_e_ir,
        args=(no["rotulo"], no["descricao"]),
    )


def _render_pendentes(pendentes: list[dict]) -> None:
    st.header(f"⏳ POPs pendentes ({len(pendentes)})")
    if not pendentes:
        st.success("Todas as etapas do fluxo já possuem POP.")
        return
    _render_grade(pendentes, "pendente", _corpo_card_pendente)


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
        botao_docx(gerar_docx(pop), pop.output_filename(), key="modelo_docx", container=col_docx)


def _abrir_preview_fluxo(pop_ref: str) -> None:
    st.session_state[SessionKey.PREVIEW] = {"tipo": "fluxo", "ref": pop_ref}


def _abrir_preview_salvo(pop_id: str) -> None:
    st.session_state[SessionKey.PREVIEW] = {"tipo": "salvo", "ref": pop_id}


def _editar_pop_salvo(pop_id: str) -> None:
    pop = get_pop(pop_id)
    if pop is None:
        return
    set_loaded_from(pop_id)
    preencher_formulario(pop)
    _ir_para_formulario()


def _editar_preview_e_ir(pop: PopData, pop_id: str | None = None) -> None:
    """Fecha a preview e abre o POP no formulário (pop_id = registro salvo)."""
    fechar_preview()
    if pop_id is not None:
        set_loaded_from(pop_id)
    _editar_pop_e_ir(pop)


def _render_preview_ativa() -> None:
    """Renderiza o POP em preview (fluxo ou salvo); limpa estado se inválido."""
    estado = get_preview_estado()
    if estado is None:
        return
    if estado.get("tipo") == "salvo":
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


def _corpo_card_salvo(record: dict) -> None:
    pop_id = record["id"]
    if st.button(
        "Visualizar",
        key=f"ver_salvo_{pop_id}",
        on_click=_abrir_preview_salvo,
        args=(pop_id,),
    ):
        pass
    col_docx, col_pdf, col_editar = st.columns(3)
    docx_bytes = get_docx_bytes(pop_id)
    if docx_bytes is not None:
        botao_docx(docx_bytes, record["filename"], key=f"docx_salvo_{pop_id}", container=col_docx)
    pop = get_pop(pop_id)
    if pop is not None:
        botao_pdf(gerar_pdf(pop), record["filename"], key=f"pdf_salvo_{pop_id}", container=col_pdf)
    col_editar.button(
        "Editar",
        key=f"editar_salvo_{pop_id}",
        on_click=_editar_pop_salvo,
        args=(pop_id,),
    )
    if st.session_state.get(CONFIRM_EXCLUIR_KEY) == pop_id:
        confirmar_exclusao(record)
    elif st.columns([3, 1])[1].button(
        "Excluir",
        key=f"excluir_salvo_{pop_id}",
        help="Remove o POP do histórico (não pode ser desfeito).",
    ):
        st.session_state[CONFIRM_EXCLUIR_KEY] = pop_id
        st.rerun()


def _render_salvos(registros: list[dict]) -> None:
    st.header(f"🗂️ POPs salvos no app ({len(registros)})")
    if not registros:
        st.caption("Nenhum POP salvo ainda. Gere um POP no formulário para vê-lo aqui.")
        return
    _render_grade(registros, "gerado", _corpo_card_salvo)


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
    registros = list_pops()

    _render_hero(fluxo, total, len(gerados), len(pendentes), len(registros))
    _render_stepper(fluxo)
    _render_modelo()
    _render_gerados(gerados, total)
    _render_pendentes(pendentes)
    _render_salvos(registros)
