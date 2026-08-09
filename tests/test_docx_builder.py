from docx import Document
from docx.oxml.ns import qn

from gerapop.constants import ValidationMessage
from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.docx.styles import set_cell_shading


def test_set_cell_shading_nao_duplica() -> None:
    doc = Document()
    cell = doc.add_table(rows=1, cols=1).rows[0].cells[0]

    set_cell_shading(cell, "D9D9D9")
    set_cell_shading(cell, "D9D9D9")

    assert len(cell._tc.get_or_add_tcPr().findall(qn("w:shd"))) == 1


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


def _docx_estrutura(pop: PopData) -> tuple[list[str], list]:
    doc = Document(__import__("io").BytesIO(gerar_docx(pop).getvalue()))
    return [p.text for p in doc.paragraphs if p.text.strip()], doc.tables


def _texto_tabela(table) -> str:
    return table.rows[0].cells[0].text


def test_numercao_plana_e_aviso_no_escopo(pop_minimo: PopData) -> None:
    pop_minimo.aviso = "Este POP não contempla o anúncio do navio."
    pop_minimo.secoes = [
        {"titulo": "Acesso ao Módulo de Manobras", "passos": ["Abrir o sistema."]},
        {"titulo": "Procedimento – Atracação", "passos": ["Localizar o navio."]},
    ]

    texts, tables = _docx_estrutura(pop_minimo)

    assert texts[2:6] == [
        "1.  Objetivo",
        "Padronizar o registro de manobras.",
        "2.  Escopo e Pré-condições",
        "Aplica-se à equipe de operações.",
    ]
    assert "3.  Definições" in texts
    assert "4.  Acesso ao Módulo de Manobras" in texts
    assert "5.  Procedimento – Atracação" in texts
    assert "6.  Regras e Restrições" in texts
    assert "7.  Consulta e Relatórios" in texts
    assert "8.  Histórico de Revisões" in texts
    assert "4.1" not in " ".join(texts)

    aviso_table = next(t for t in tables if "ATENÇÃO" in _texto_tabela(t))
    assert _texto_tabela(aviso_table) == "⚠ ATENÇÃO: Este POP não contempla o anúncio do navio."

    regra_table = next(t for t in tables if len(t.columns) == 2 and _texto_tabela(t) == "R")
    assert regra_table.rows[0].cells[1].text == "Não executar sem autorização."

    consulta_table = next(t for t in tables if len(t.columns) == 1 and "Menu" in _texto_tabela(t))
    assert consulta_table.rows[0].cells[0].text == "Menu > Operações > Manobras"


def test_aviso_vem_depois_do_escopo(pop_minimo: PopData) -> None:
    pop_minimo.aviso = "Procedimento condicionado."

    doc = Document(__import__("io").BytesIO(gerar_docx(pop_minimo).getvalue()))
    seq: list[str] = []
    for child in doc.element.body:
        if child.tag == qn("w:p"):
            text = "".join(node.text or "" for node in child.iter(qn("w:t"))).strip()
            if text:
                seq.append(text)
        elif child.tag == qn("w:tbl"):
            text = "".join(node.text or "" for node in child.iter(qn("w:t"))).strip()
            if text:
                seq.append(text)

    escopo = seq.index("Aplica-se à equipe de operações.")
    assert seq[escopo + 1] == "⚠ ATENÇÃO: Procedimento condicionado."
