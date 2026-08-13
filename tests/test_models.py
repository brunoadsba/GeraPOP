import re

from gerapop.constants import ValidationMessage
from gerapop.models import PopData, default_revisao


def test_validate_retorna_lista_vazia_quando_valido(pop_minimo: PopData) -> None:
    assert pop_minimo.validate() == []


def test_default_revisao_preenchida() -> None:
    revisao = default_revisao()

    assert revisao["revisao"] == "01"
    assert revisao["descricao"] == "Emissão inicial"
    assert revisao["data"]


def test_from_form_normaliza_espacos() -> None:
    pop = PopData.from_form(
        nome_pop="  Nome  ",
        codigo="  COD  ",
        versao="01",
        data="01/01/2026",
        area="  Área  ",
        aviso="  aviso  ",
        objetivo="  objetivo  ",
        escopo="  escopo  ",
        definicoes=[],
        secoes=[],
        regras=[],
        consulta="  consulta  ",
        revisoes=[],
    )

    assert pop.nome_pop == "Nome"
    assert pop.codigo == "COD"
    assert pop.consulta == "consulta"


def test_validate_mensagens(pop_invalido: PopData) -> None:
    errors = pop_invalido.validate()

    assert len(errors) == 4
    assert all(isinstance(message, ValidationMessage) for message in errors)


def test_output_filename_sanitiza_caracteres_invalidos(pop_minimo: PopData) -> None:
    pop_minimo.nome_pop = "POP: OPE?1*"

    assert pop_minimo.output_filename() == "POP-OPE-001_POP_OPE_1.docx"


def test_output_filename_somente_whitelist(pop_minimo: PopData) -> None:
    pop_minimo.nome_pop = "Manobras / Desembarque (tarde) — urgente"

    slug = pop_minimo.output_filename().split("_", 1)[1].removesuffix(".docx")
    assert re.fullmatch(r"[\w.-]+", slug)


def test_output_filename_preserva_acentos(pop_minimo: PopData) -> None:
    pop_minimo.codigo = "POP-PS-002"
    pop_minimo.nome_pop = "PS - Programação de Saída"

    assert pop_minimo.output_filename() == "POP-PS-002_PS_-_Programação_de_Saída.docx"


def test_output_filename_sem_underscores_nas_borbas(pop_minimo: PopData) -> None:
    pop_minimo.nome_pop = "  Operações Portuárias  "

    filename = pop_minimo.output_filename()
    assert "  " not in filename
    assert not filename.endswith("_.docx")
