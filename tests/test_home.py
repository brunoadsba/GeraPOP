"""Testes da tela inicial (home): classificação gerados/pendentes e navegação.

Unit: `classificar_nos` e `carregar_fluxo` (funções puras).
E2E: a home abre por padrão, "Criar POP" pré-preenche o formulário e
"Editar POP" carrega o POP vinculado do fluxo.
"""

from conftest import APP_PATH
from streamlit.testing.v1 import AppTest

from gerapop.constants import SessionKey
from gerapop.ui import home

NOME_POP_DESEMBARQUE = "Manobra de Atracação de Navio"


def _fluxo_fixture() -> dict:
    return {
        "fluxo_id": "desembarque",
        "titulo": "Fluxo — Desembarque",
        "nos": [
            {"id": "planejamento", "etapa": 2, "rotulo": "Planejamento", "pop_ref": None},
            {"id": "atracacao", "etapa": 1, "rotulo": "Atracação", "pop_ref": "pop-x"},
            {"id": "chegada", "etapa": 3, "rotulo": "Chegada", "pop_ref": None},
            {"id": "desatracacao", "etapa": 4, "rotulo": "Desatracação", "pop_ref": "pop-x"},
        ],
    }


def test_classificar_nos_separa_e_ordena() -> None:
    pendentes, gerados = home.classificar_nos(_fluxo_fixture())
    assert [no["rotulo"] for no in pendentes] == ["Planejamento", "Chegada"]
    assert [no["rotulo"] for no in gerados] == ["Atracação", "Desatracação"]


def test_classificar_nos_sem_nos() -> None:
    assert home.classificar_nos({}) == ([], [])


def test_carregar_fluxo_inexistente_retorna_none(tmp_path) -> None:
    assert home.carregar_fluxo(tmp_path / "nao-existe.json") is None


def test_carregar_fluxo_invalido_retorna_none(tmp_path) -> None:
    path = tmp_path / "fluxo.json"
    path.write_text("{corrompido", encoding="utf-8")
    assert home.carregar_fluxo(path) is None


def test_carregar_fluxo_do_repositorio() -> None:
    fluxo = home.carregar_fluxo()
    assert fluxo is not None
    assert len(fluxo["nos"]) == 7


def test_home_abre_por_padrao() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    assert not at.exception
    assert at.sidebar.radio[0].value == home.PAGINA_HOME
    assert any("POPs pendentes" in el.value for el in at.header)


def test_home_criar_pop_preenche_formulario() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    at.button(key="criar_chegada").click()
    at.run()

    assert not at.exception
    assert at.sidebar.radio[0].value == home.PAGINA_FORM
    assert at.text_input(key="nome_pop").value == "Chegada do navio"
    assert at.text_area(key="objetivo").value == (
        "Recebimento do aviso de ETA e identificação do navio."
    )


def test_home_editar_pop_carrega_formulario() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    at.button(key="editar_atracacao").click()
    at.run()

    assert not at.exception
    assert at.sidebar.radio[0].value == home.PAGINA_FORM
    assert at.text_input(key="nome_pop").value == NOME_POP_DESEMBARQUE
    assert at.session_state[SessionKey.CODIGO] == "POP-MAN-001"


def test_home_visualizar_pop_abre_preview() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    at.button(key="ver_atracacao").click()
    at.run()

    assert not at.exception
    assert any(NOME_POP_DESEMBARQUE in el.value for el in at.markdown)
    assert any("Objetivo" in el.value for el in at.markdown)
    assert at.button(key="preview_voltar") is not None
    assert at.button(key="preview_editar") is not None
    assert len(at.get("download_button")) >= 2


def test_home_preview_voltar_retorna_ao_painel() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    at.button(key="ver_atracacao").click()
    at.run()
    assert at.button(key="preview_voltar") is not None

    at.button(key="preview_voltar").click()
    at.run()

    assert not at.exception
    assert any("POPs pendentes" in el.value for el in at.header)
    assert not any(btn.key == "preview_voltar" for btn in at.button)
