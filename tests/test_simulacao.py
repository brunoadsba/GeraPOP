"""Testes da simulação de preenchimento, flags de orientação e modelo.

Unit: `passos_simulacao` (sequência/chaves) e `EXEMPLO` (dados validáveis).
E2E: simulação completa preenche o formulário, "Parar" interrompe no meio,
flags renderizadas e modelo de referência carrega no formulário (form e home).
"""

import pytest
from conftest import APP_PATH, _abrir_formulario
from streamlit.testing.v1 import AppTest

from gerapop.constants import SessionKey
from gerapop.models import PopData
from gerapop.ui import home, simulacao


@pytest.fixture(autouse=True)
def _sim_sleep_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(simulacao, "SIM_SLEEP", 0.0)


# --- unit ---


def test_passos_simulacao_sequencia() -> None:
    passos = simulacao.passos_simulacao()
    chaves = [chave for chave, _ in passos]
    assert chaves[0] == SessionKey.NOME_POP
    assert SessionKey.CODIGO in chaves
    assert SessionKey.OBJETIVO in chaves
    assert SessionKey.SECOES in chaves
    assert len(passos) >= 12


def test_exemplo_validavel() -> None:
    e = simulacao.EXEMPLO
    pop = PopData.from_form(
        nome_pop=e["nome_pop"],
        codigo=e["codigo"],
        versao=e["versao"],
        data=e["data"],
        area=e["area"],
        aviso=e["aviso"],
        objetivo=e["objetivo"],
        escopo=e["escopo"],
        definicoes=e["definicoes"],
        secoes=[e["secao_1"], e["secao_2"]],
        regras=e["regras"],
        consulta=e["consulta"],
        revisoes=e["revisoes"],
    )
    assert pop.validate() == []


# --- e2e ---


def test_e2e_simulacao_completa_preenche_formulario() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _abrir_formulario(at)

    at.button(key="sim_iniciar").click()
    for _ in range(40):
        at.run()
        if SessionKey.SIM_ACTIVE not in at.session_state:
            break

    assert not at.exception
    assert any("Simulação concluída" in s.value for s in at.success)
    assert at.session_state[SessionKey.NOME_POP] == "Manobra de Atracação de Navio"
    assert at.session_state[SessionKey.CODIGO] == "POP-MAN-001"
    assert len(at.session_state[SessionKey.DEFINICOES]) == 3
    assert len(at.session_state[SessionKey.SECOES]) == 2
    assert len(at.session_state[SessionKey.REVISOES]) == 2


def test_e2e_simulacao_parar_no_meio(monkeypatch: pytest.MonkeyPatch) -> None:
    # O AppTest honra st.rerun() re-executando o script até o fim, então a
    # simulação inteira completaria em um único at.run(). Neutralizamos o
    # rerun para avançar passo a passo e poder clicar em "Parar" no meio.
    monkeypatch.setattr(simulacao.st, "rerun", lambda: None)
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _abrir_formulario(at)

    at.button(key="sim_iniciar").click()
    at.run()  # passo 0: nome_pop
    at.run()  # passo 1: codigo

    assert any(b.key == "sim_parar" for b in at.button)
    at.button(key="sim_parar").click()
    at.run()

    assert not at.exception
    assert SessionKey.SIM_ACTIVE not in at.session_state
    assert SessionKey.SIM_STEP not in at.session_state
    assert at.session_state[SessionKey.NOME_POP] == "Manobra de Atracação de Navio"
    assert at.session_state[SessionKey.CODIGO] == "POP-MAN-001"
    assert at.session_state[SessionKey.OBJETIVO] == ""


def test_e2e_flags_de_orientacao_renderizadas() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _abrir_formulario(at)

    marcas = " ".join(el.value for el in at.markdown)
    assert "OBRIGATÓRIO" in marcas
    assert "OPCIONAL" in marcas


def test_e2e_modelo_carrega_no_formulario() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _abrir_formulario(at)

    at.button(key="modelo_btn").click()
    at.run()

    assert not at.exception
    assert at.text_input(key="nome_pop").value == "Manobra de Atracação de Navio"
    assert at.session_state[SessionKey.CODIGO] == "POP-MAN-001"
    assert len(at.session_state[SessionKey.SECOES]) == 2


def test_e2e_modelo_disponivel_na_home() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    assert any("Modelo de referência" in el.value for el in at.header)
    at.button(key="modelo_ver").click()
    at.run()

    assert not at.exception
    assert at.sidebar.radio[0].value == home.PAGINA_FORM
    assert at.text_input(key="nome_pop").value == "Manobra de Atracação de Navio"
