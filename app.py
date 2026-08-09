"""Interface Streamlit do GeraPOP."""

from datetime import date

import streamlit as st

from gerapop.docx_builder import gerar_docx
from gerapop.models import PopData
from gerapop.session import (
    add_item,
    add_passo,
    get_definicoes,
    get_regras,
    get_revisoes,
    get_secoes,
    init_state,
    remove_item,
    remove_passo,
)

st.set_page_config(page_title="GeraPOP - CODEBA", page_icon="📋", layout="centered")

init_state()


def render_form() -> PopData | None:
    st.title("GeraPOP — CODEBA")
    st.caption("Preencha os campos e gere o documento POP formatado (.docx).")

    st.header("Identificação")
    col1, col2 = st.columns(2)
    with col1:
        nome_pop = st.text_input(
            "Nome do POP *",
            placeholder="Registro de Manobras no Sistema TOS – OpenPort",
        )
        codigo = st.text_input("Código *", placeholder="POP-OPE-XXX")
        versao = st.text_input("Versão", value="01")
    with col2:
        area = st.text_input("Área *", placeholder="Operações Portuárias")
        data_pop = st.text_input("Data", value=date.today().strftime("%d/%m/%Y"))

    aviso = st.text_input(
        "Aviso / Atenção (opcional)",
        placeholder="Ex: Este POP não contempla...",
    )

    st.header("1. Objetivo")
    objetivo = st.text_area("Descreva o objetivo do procedimento *", height=100)

    st.header("2. Escopo e Pré-condições")
    escopo = st.text_area("A quem se aplica / condições prévias", height=100)

    st.header("3. Definições")
    for i, item in enumerate(get_definicoes()):
        c1, c2, c3 = st.columns([2, 4, 1])
        item["termo"] = c1.text_input(
            "Termo",
            value=item["termo"],
            key=f"termo_{i}",
            label_visibility="collapsed",
            placeholder="Termo",
        )
        item["definicao"] = c2.text_input(
            "Definição",
            value=item["definicao"],
            key=f"def_{i}",
            label_visibility="collapsed",
            placeholder="Definição",
        )
        if c3.button("Remover", key=f"rm_def_{i}"):
            remove_item("definicoes", i)
            st.rerun()
    st.button(
        "+ Adicionar termo",
        on_click=add_item,
        args=("definicoes", {"termo": "", "definicao": ""}),
    )

    st.header("4. Procedimento")
    for si, sec in enumerate(get_secoes()):
        st.subheader(f"Seção {si + 1}")
        sec["titulo"] = st.text_input(
            "Título da seção",
            value=sec["titulo"],
            key=f"sec_titulo_{si}",
            placeholder="Ex: Procedimento – Atracação",
        )
        for pi, passo in enumerate(sec["passos"]):
            c1, c2 = st.columns([6, 1])
            sec["passos"][pi] = c1.text_input(
                f"Passo {pi + 1}",
                value=passo,
                key=f"passo_{si}_{pi}",
                label_visibility="collapsed",
                placeholder=f"Passo {pi + 1}",
            )
            if c2.button("Remover", key=f"rm_passo_{si}_{pi}"):
                remove_passo(si, pi)
                st.rerun()
        st.button("+ Adicionar passo", key=f"add_passo_{si}", on_click=add_passo, args=(si,))
        if len(get_secoes()) > 1 and st.button("Remover seção", key=f"rm_sec_{si}"):
            remove_item("secoes", si)
            st.rerun()
        st.divider()
    st.button(
        "+ Adicionar seção",
        on_click=add_item,
        args=("secoes", {"titulo": "", "passos": [""]}),
    )

    st.header("5. Regras e Restrições")
    regras = get_regras()
    for i, regra in enumerate(regras):
        c1, c2 = st.columns([6, 1])
        regras[i] = c1.text_input(
            "Regra",
            value=regra,
            key=f"regra_{i}",
            label_visibility="collapsed",
            placeholder="Regra",
        )
        if c2.button("Remover", key=f"rm_regra_{i}"):
            remove_item("regras", i)
            st.rerun()
    st.button("+ Adicionar regra", on_click=add_item, args=("regras", ""))

    st.header("6. Consulta e Relatórios")
    consulta = st.text_area("Caminho / menu para consulta (opcional)", height=70)

    st.header("7. Histórico de Revisões")
    for i, rev in enumerate(get_revisoes()):
        c1, c2, c3, c4 = st.columns([1, 1.5, 4, 2])
        rev["revisao"] = c1.text_input(
            "Rev.",
            value=rev["revisao"],
            key=f"rev_{i}",
            label_visibility="collapsed",
        )
        rev["data"] = c2.text_input(
            "Data",
            value=rev["data"],
            key=f"revdata_{i}",
            label_visibility="collapsed",
        )
        rev["descricao"] = c3.text_input(
            "Descrição",
            value=rev["descricao"],
            key=f"revdesc_{i}",
            label_visibility="collapsed",
            placeholder="Descrição",
        )
        rev["responsavel"] = c4.text_input(
            "Responsável",
            value=rev["responsavel"],
            key=f"revresp_{i}",
            label_visibility="collapsed",
            placeholder="Responsável",
        )
    st.button(
        "+ Adicionar revisão",
        on_click=add_item,
        args=("revisoes", {"revisao": "", "data": "", "descricao": "", "responsavel": ""}),
    )

    st.divider()

    if st.button("Gerar POP (.docx)", type="primary"):
        pop = PopData.from_form(
            nome_pop=nome_pop,
            codigo=codigo,
            versao=versao,
            data=data_pop,
            area=area,
            aviso=aviso,
            objetivo=objetivo,
            escopo=escopo,
            definicoes=get_definicoes(),
            secoes=get_secoes(),
            regras=get_regras(),
            consulta=consulta,
            revisoes=get_revisoes(),
        )
        errors = pop.validate()
        if errors:
            for error in errors:
                st.error(error)
            return None

        st.session_state["generated_pop"] = pop
        st.rerun()

    return None


def render_download() -> None:
    pop: PopData | None = st.session_state.get("generated_pop")
    if not pop:
        return

    st.success("POP gerado com sucesso.")
    buf = gerar_docx(pop)
    st.download_button(
        "Baixar POP (.docx)",
        data=buf,
        file_name=pop.output_filename(),
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )


render_form()
render_download()
