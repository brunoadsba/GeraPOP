import logging
from datetime import date
from pathlib import Path

import pytest

from gerapop.models import PopData

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")


def _button(at, label: str):
    buttons = [button for button in at.button if button.label == label]
    if not buttons:
        raise AssertionError(f"Botão '{label}' não encontrado no AppTest")
    return buttons[0]


def _abrir_formulario(at) -> None:
    """Garante que a tela atual seja o formulário (navega a partir da home)."""
    radios = [radio for radio in at.sidebar.radio if radio.label == "Navegação"]
    if radios and radios[0].value != "📝 Formulário":
        radios[0].set_value("📝 Formulário")
        at.run()


def _fill_obrigatorios(at) -> None:
    """Preenche os campos obrigatórios usando as chaves dos widgets."""
    at.text_input(key="nome_pop").set_value("Registro de Manobras no Sistema TOS")
    at.text_input(key="codigo").set_value("POP-OPE-001")
    at.text_input(key="area").set_value("Operações Portuárias")
    at.text_area(key="objetivo").set_value("Padronizar o registro de manobras.")


def _gerar_pop(at) -> None:
    _button(at, "Gerar POP (.docx)").click()
    at.run()


def _download_pop_atual(at) -> list:
    return [d for d in at.get("download_button") if d.proto.label == "Baixar POP (.docx)"]


def _download_pdf_gerado(at) -> list:
    return [d for d in at.get("download_button") if d.proto.label == "Baixar POP (.pdf)"]


def _download_json_historico(at) -> list:
    return [d for d in at.get("download_button") if d.proto.label == "Baixar .pdf"]


@pytest.fixture(autouse=True)
def _data_dir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GERAPOP_DATA_DIR", str(tmp_path))


@pytest.fixture
def pop_minimo() -> PopData:
    return PopData(
        nome_pop="Registro de Manobras",
        codigo="POP-OPE-001",
        versao="01",
        data=date.today().strftime("%d/%m/%Y"),
        area="Operações Portuárias",
        aviso="",
        objetivo="Padronizar o registro de manobras.",
        escopo="Aplica-se à equipe de operações.",
        definicoes=[{"termo": "TOS", "definicao": "Terminal Operating System"}],
        secoes=[
            {
                "titulo": "Atracação",
                "passos": ["Verificar condições.", "Registrar no sistema."],
            }
        ],
        regras=["Não executar sem autorização."],
        consulta="Menu > Operações > Manobras",
        revisoes=[
            {
                "revisao": "01",
                "data": "01/01/2026",
                "descricao": "Emissão inicial",
                "responsavel": "Operações",
            }
        ],
    )


@pytest.fixture
def pop_invalido() -> PopData:
    return PopData(
        nome_pop="",
        codigo="",
        versao="01",
        data="01/01/2026",
        area="",
        aviso="",
        objetivo="",
        escopo="",
    )
