import logging
from datetime import date

import pytest

from gerapop.models import PopData

logging.getLogger("streamlit.runtime.scriptrunner_utils.script_run_context").setLevel(logging.ERROR)


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
