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
