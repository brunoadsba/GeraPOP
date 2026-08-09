"""Testes E2E do app Streamlit usando AppTest (streamlit.testing.v1).

Executa o fluxo real da interface: preencher formulario, clicar em gerar e
verificar o `.docx` produzido (mesmo caminho servido pelo botao de download).
"""

from io import BytesIO
from pathlib import Path

from docx import Document
from streamlit.testing.v1 import AppTest

from gerapop.constants import SessionKey, ValidationMessage
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _button(at: AppTest, label: str):
    return [button for button in at.button if button.label == label][0]


def _fill_obrigatorios(at: AppTest) -> None:
    at.text_input[0].set_value("Registro de Manobras no Sistema TOS")  # Nome do POP
    at.text_input[1].set_value("POP-OPE-001")  # Código
    at.text_input[3].set_value("Operações Portuárias")  # Área
    at.text_area[0].set_value("Padronizar o registro de manobras.")  # Objetivo


def _gerar_pop(at: AppTest) -> None:
    _button(at, "Gerar POP (.docx)").click()
    at.run()


def _docx_texts(pop: PopData) -> list[str]:
    doc = Document(BytesIO(gerar_docx(pop).getvalue()))
    texts = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            texts.extend(cell.text for cell in row.cells)
    return texts


def test_e2e_fluxo_completo_gera_docx() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    _fill_obrigatorios(at)
    _gerar_pop(at)

    assert not at.exception
    assert [success.value for success in at.success] == ["POP gerado com sucesso."]

    download = at.get("download_button")
    assert len(download) == 1
    assert download[0].proto.label == "Baixar POP (.docx)"

    pop = at.session_state[SessionKey.GENERATED_POP]
    assert pop.validate() == []
    # slug truncado em 30 chars
    assert pop.output_filename() == "POP-OPE-001_Registro_de_Manobras_no_Sistem.docx"

    texts = _docx_texts(pop)
    assert "Registro de Manobras no Sistema TOS" in texts
    assert "POP-OPE-001" in texts
    assert "Operações Portuárias" in texts
    assert "Padronizar o registro de manobras." in texts


def test_e2e_validacao_impede_geracao() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    _gerar_pop(at)

    assert not at.exception
    assert not at.success
    assert at.get("download_button") == []

    errors = [error.value for error in at.error]
    assert len(errors) == 4
    assert ValidationMessage.NOME_OBRIGATORIO in errors
    assert ValidationMessage.CODIGO_OBRIGATORIO in errors
    assert ValidationMessage.AREA_OBRIGATORIA in errors
    assert ValidationMessage.OBJETIVO_OBRIGATORIO in errors

    assert SessionKey.GENERATED_POP not in at.session_state


def test_e2e_listas_dinamicas_integradas() -> None:
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    _button(at, "+ Adicionar termo").click()
    at.run()
    at.text_input(key="termo_1").set_value("TOS")
    at.text_input(key="def_1").set_value("Terminal Operating System")

    at.text_input(key="sec_titulo_0").set_value("Atracação")
    at.text_input(key="passo_0_0").set_value("Verificar condições.")
    _button(at, "+ Adicionar passo").click()
    at.run()
    at.text_input(key="passo_0_1").set_value("Registrar no sistema.")

    _button(at, "+ Adicionar regra").click()
    at.run()
    at.text_input(key="regra_1").set_value("Não executar sem autorização.")

    _button(at, "+ Adicionar revisão").click()
    at.run()
    at.text_input(key="rev_1").set_value("02")
    at.text_input(key="revdesc_1").set_value("Revisão geral")

    _fill_obrigatorios(at)
    _gerar_pop(at)

    assert not at.exception
    assert [success.value for success in at.success] == ["POP gerado com sucesso."]

    pop = at.session_state[SessionKey.GENERATED_POP]
    texts = _docx_texts(pop)
    assert "TOS" in texts
    assert "Terminal Operating System" in texts
    assert "4.1.  Atracação" in texts
    assert "Verificar condições." in texts
    assert "Registrar no sistema." in texts
    assert "Não executar sem autorização." in texts
    assert "Revisão geral" in texts
