from gerapop.constants import ValidationMessage
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx


def test_gerar_docx_minimo(pop_minimo: PopData) -> None:
    content = gerar_docx(pop_minimo).getvalue()

    assert content[:2] == b"PK"
    assert len(content) > 1000


def test_validacao_campos_obrigatorios(pop_invalido: PopData) -> None:
    errors = pop_invalido.validate()

    assert ValidationMessage.NOME_OBRIGATORIO in errors
    assert ValidationMessage.OBJETIVO_OBRIGATORIO in errors
    assert ValidationMessage.CODIGO_OBRIGATORIO in errors
    assert ValidationMessage.AREA_OBRIGATORIA in errors


def test_output_filename(pop_minimo: PopData) -> None:
    pop_minimo.nome_pop = "Registro de Manobras no Sistema"

    assert pop_minimo.output_filename().startswith("POP-OPE-001_")
    assert pop_minimo.output_filename().endswith(".docx")
