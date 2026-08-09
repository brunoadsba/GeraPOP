"""Testes E2E da unicidade de código de POP (Opção A).

Cobre: bloqueio em sessão independente, regeração do mesmo formulário na
mesma sessão e o fluxo "Carregar para editar" → editar → regerar (com a
marca de código repetido no histórico).
"""

from conftest import APP_PATH, _button, _fill_obrigatorios, _gerar_pop
from streamlit.testing.v1 import AppTest

from gerapop.constants import SessionKey
from gerapop.storage import clear_draft, list_pops


def test_e2e_codigo_duplicado_bloqueia_nova_sessao() -> None:
    at1 = AppTest.from_file(APP_PATH, default_timeout=10)
    at1.run()
    _fill_obrigatorios(at1)
    _gerar_pop(at1)
    assert len(list_pops()) == 1

    # Sessão nova (rascunho limpo) não herda a origem do formulário anterior.
    clear_draft()

    at2 = AppTest.from_file(APP_PATH, default_timeout=10)
    at2.run()
    _fill_obrigatorios(at2)
    at2.text_input[0].set_value("Outro POP com o mesmo código")
    _gerar_pop(at2)

    assert not at2.exception
    assert not at2.success
    assert SessionKey.GENERATED_POP not in at2.session_state
    assert [d for d in at2.get("download_button") if d.proto.label == "Baixar POP (.docx)"] == []

    errors = [error.value for error in at2.error]
    assert any("POP-OPE-001" in error and "já é usado" in error for error in errors)
    assert len(list_pops()) == 1


def test_e2e_regerar_mesmo_form_permitido() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _fill_obrigatorios(at)
    _gerar_pop(at)
    assert at.success

    at.text_input[0].set_value("Registro de Manobras no Sistema TOS (edição)")
    at.run()
    assert SessionKey.GENERATED_POP not in at.session_state

    _gerar_pop(at)

    assert not at.exception
    assert not at.error
    assert [success.value for success in at.success] == ["POP gerado com sucesso."]
    assert SessionKey.GENERATED_POP in at.session_state
    assert len(list_pops()) == 2


def test_e2e_carregar_editar_regerar_com_marca() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    _fill_obrigatorios(at)
    _gerar_pop(at)
    at.run()  # re-render limpo após o st.rerun

    _button(at, "Carregar para editar").click()
    at.run()
    at.run()  # re-render limpo após o st.rerun do carregamento

    at.text_area[0].set_value("Objetivo revisado após carregar")
    at.run()
    _gerar_pop(at)
    at.run()

    assert not at.exception
    assert not at.error
    assert [success.value for success in at.success] == ["POP gerado com sucesso."]

    records = list_pops()
    assert len(records) == 2
    assert all(record["codigo"] == "POP-OPE-001" for record in records)
    assert any("⚠" in option for option in at.selectbox[0].options)
