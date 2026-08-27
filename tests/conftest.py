from datetime import date
from pathlib import Path

import pytest

from gerapop.models import PopData


@pytest.fixture(autouse=True)
def _data_dir_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GERAPOP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("GERAPOP_LIBRARY_DIR", str(tmp_path / "biblioteca"))


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
