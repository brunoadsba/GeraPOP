"""Simulação de preenchimento — preenche o formulário campo a campo.

Usa o POP modelo (Manobra de Atracação de Navio) como exemplo didático:
cada tick da simulação preenche um campo do formulário, mostrando ao
usuário como cada campo deve ser preenchido. O usuário pode parar a
qualquer momento com o botão "Parar simulação".
"""

from __future__ import annotations

import os
import random
import time
from copy import deepcopy
from typing import Any

import streamlit as st

from gerapop.constants import SessionKey
from gerapop.session import reset_widgets_formulario

SIM_SLEEP = float(os.environ.get("GERAPOP_SIM_SLEEP", "0.9"))

_CAMPO_LABEL: dict[SessionKey, str] = {
    SessionKey.NOME_POP: "Nome do POP",
    SessionKey.CODIGO: "Código",
    SessionKey.VERSAO: "Versão",
    SessionKey.DATA: "Data de emissão",
    SessionKey.AREA: "Área",
    SessionKey.AVISO: "Aviso / Atenção",
    SessionKey.OBJETIVO: "Objetivo",
    SessionKey.ESCOPO: "Escopo",
    SessionKey.DEFINICOES: "Definições",
    SessionKey.SECOES: "Procedimento",
    SessionKey.REGRAS: "Regras",
    SessionKey.CONSULTA: "Consulta",
    SessionKey.REVISOES: "Revisões",
}

# Exemplo didático — mesmo conteúdo do POP modelo "Manobra de Atracação de Navio".
EXEMPLO: dict[str, Any] = {
    "nome_pop": "Manobra de Atracação de Navio",
    "codigo": "POP-MAN-001",
    "versao": "02",
    "data": "15/03/2026",
    "area": "Operações Portuárias",
    "aviso": (
        "Manobra de atracação somente com prático credenciado a bordo e " "rebocadores disponíveis."
    ),
    "objetivo": (
        "Padronizar a manobra de atracação de navios no berço designado, "
        "garantindo segurança à tripulação, ao navio e à infraestrutura do terminal."
    ),
    "escopo": (
        "Aplica-se à equipe de operações portuárias, práticos, rebocadores e "
        "conferentes envolvidos na manobra de atracação."
    ),
    "definicoes": [
        {
            "termo": "Prático",
            "definicao": "Profissional credenciado responsável por conduzir a manobra do navio.",
        },
        {
            "termo": "Rebocador",
            "definicao": "Embarcação de apoio usada para posicionar o navio durante a atracação.",
        },
        {
            "termo": "Berço",
            "definicao": "Local designado no cais onde o navio será atracado.",
        },
    ],
    "secao_1": {
        "titulo": "Preparação da manobra",
        "passos": [
            "Confirmar o horário de chegada (ETA) e a identificação do navio.",
            "Designar o berço de atracação conforme o plano de operação.",
            "Confirmar a disponibilidade de prático e rebocadores.",
        ],
        "campos": [
            {"campo": "Data e Hora", "descricao": "Data e hora efetiva do início da manobra."},
            {"campo": "Berço", "descricao": "Número do berço designado para a atracação."},
            {"campo": "Prático", "descricao": "Nome do prático responsável pela manobra."},
        ],
    },
    "secao_2": {
        "titulo": "Execução da atracação",
        "passos": [
            "Conduzir o navio até o berço com apoio dos rebocadores.",
            "Posicionar o navio conforme o plano de manobra.",
            "Passar as amarras e fixar o navio ao cais.",
            "Confirmar a atracação e registrar o término da manobra.",
        ],
        "campos": [
            {"campo": "Rebocadores", "descricao": "Relação dos rebocadores utilizados na manobra."},
        ],
    },
    "regras": [
        "Não iniciar a manobra sem prático credenciado a bordo.",
        "Manter comunicação de rádio contínua entre prático, rebocadores e coordenação.",
        "Parar a manobra imediatamente em caso de condição meteorológica adversa.",
    ],
    "consulta": "Menu > Operações > Manobras",
    "revisoes": [
        {
            "revisao": "02",
            "data": "15/03/2026",
            "descricao": "Inclusão dos campos obrigatórios de registro da manobra.",
            "responsavel": "Operações Portuárias",
        },
        {
            "revisao": "01",
            "data": "10/01/2026",
            "descricao": "Emissão inicial.",
            "responsavel": "Operações Portuárias",
        },
    ],
}


def passos_simulacao() -> list[tuple[SessionKey, Any]]:
    """Sequência de passos: cada passo preenche um campo (ou bloco) do formulário."""
    e = EXEMPLO
    return [
        (SessionKey.NOME_POP, e["nome_pop"]),
        (SessionKey.CODIGO, e["codigo"]),
        (SessionKey.VERSAO, e["versao"]),
        (SessionKey.DATA, e["data"]),
        (SessionKey.AREA, e["area"]),
        (SessionKey.AVISO, e["aviso"]),
        (SessionKey.OBJETIVO, e["objetivo"]),
        (SessionKey.ESCOPO, e["escopo"]),
        (SessionKey.DEFINICOES, deepcopy(e["definicoes"])),
        (SessionKey.SECOES, [deepcopy(e["secao_1"])]),
        (SessionKey.SECOES, [deepcopy(e["secao_1"]), deepcopy(e["secao_2"])]),
        (SessionKey.REGRAS, deepcopy(e["regras"])),
        (SessionKey.CONSULTA, e["consulta"]),
        (SessionKey.REVISOES, deepcopy(e["revisoes"])),
    ]


def _iniciar_simulacao() -> None:
    reset_widgets_formulario()
    st.session_state[SessionKey.SIM_ACTIVE] = True
    st.session_state[SessionKey.SIM_STEP] = 0


def _parar_simulacao() -> None:
    st.session_state.pop(SessionKey.SIM_ACTIVE, None)
    st.session_state.pop(SessionKey.SIM_STEP, None)


def _aplicar_passo(passo: tuple[SessionKey, Any]) -> None:
    chave, valor = passo
    st.session_state[chave] = valor


def _descricao_passo(passo: tuple[SessionKey, Any]) -> str:
    chave, valor = passo
    label = _CAMPO_LABEL.get(chave, chave)
    if isinstance(valor, str) and valor:
        return f"{label}: {valor}"
    if isinstance(valor, list) and valor:
        return f"{label}: {len(valor)} itens"
    return label


def render_simulacao() -> None:
    """Renderiza o painel de simulação e aplica o passo atual quando ativa.

    Deve ser chamado ANTES de renderizar os campos do formulário, para que
    os valores setados aqui sejam adotados pelos widgets no mesmo run.
    """
    passos = passos_simulacao()
    total = len(passos)
    ativa = bool(st.session_state.get(SessionKey.SIM_ACTIVE, False))
    passo_idx = int(st.session_state.get(SessionKey.SIM_STEP, 0))

    with st.container(border=True):
        st.markdown("**🤖 Simulação de preenchimento (RPA)**")
        if ativa:
            if passo_idx < total:
                st.caption(f"Preenchendo: {_descricao_passo(passos[passo_idx])}")
            st.button("⏹ Parar simulação", key="sim_parar", on_click=_parar_simulacao)
            st.progress(
                min(passo_idx, total) / total,
                text=f"Campo {min(passo_idx + 1, total)} de {total}",
            )
        else:
            st.caption(
                "Um robô preenche o formulário automaticamente, campo a campo, "
                "mostrando na prática como cada campo deve ser preenchido."
            )
            st.button("▶ Iniciar simulação", key="sim_iniciar", on_click=_iniciar_simulacao)

    if not ativa:
        return
    if passo_idx >= total:
        _parar_simulacao()
        st.success(
            "Simulação concluída — o formulário está preenchido com o exemplo. "
            "Revise, edite e gere o POP quando quiser."
        )
        return

    _aplicar_passo(passos[passo_idx])
    st.session_state[SessionKey.SIM_STEP] = passo_idx + 1
    time.sleep(SIM_SLEEP * random.uniform(0.6, 1.4))
    st.rerun()
