from datetime import date

from gerapop.docx_builder import gerar_docx
from gerapop.models import PopData


def test_gerar_docx_minimo() -> None:
    pop = PopData(
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

    buf = gerar_docx(pop)
    content = buf.getvalue()

    assert content[:2] == b"PK"
    assert len(content) > 1000


def test_validacao_campos_obrigatorios() -> None:
    pop = PopData(
        nome_pop="",
        codigo="",
        versao="01",
        data="01/01/2026",
        area="",
        aviso="",
        objetivo="",
        escopo="",
    )

    errors = pop.validate()
    assert "Nome do POP é obrigatório." in errors
    assert "Objetivo é obrigatório." in errors
    assert "Código é obrigatório." in errors
    assert "Área é obrigatória." in errors


def test_output_filename() -> None:
    pop = PopData(
        nome_pop="Registro de Manobras no Sistema",
        codigo="POP-OPE-001",
        versao="01",
        data="01/01/2026",
        area="Operações",
        aviso="",
        objetivo="Teste",
        escopo="",
    )
    assert pop.output_filename().startswith("POP-OPE-001_")
    assert pop.output_filename().endswith(".docx")
