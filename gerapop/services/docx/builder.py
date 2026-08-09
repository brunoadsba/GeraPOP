from __future__ import annotations

import io

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from gerapop.constants import (
    AVISO_PREFIX,
    DOCX_TITLE,
    FONT_HEADING_PT,
    FONT_SUBTITLE_PT,
    FONT_TITLE_PT,
    MARGIN_BOTTOM_CM,
    MARGIN_LEFT_CM,
    MARGIN_RIGHT_CM,
    MARGIN_TOP_CM,
    PASSO_COL_WIDTH_CM,
    SHADING_AVISO,
    SHADING_HEADER,
)
from gerapop.models import PopData
from gerapop.services.docx.styles import set_cell_shading, style_header_cell


def _configure_margins(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Cm(MARGIN_TOP_CM)
        section.bottom_margin = Cm(MARGIN_BOTTOM_CM)
        section.left_margin = Cm(MARGIN_LEFT_CM)
        section.right_margin = Cm(MARGIN_RIGHT_CM)


def _add_centered_title(doc: Document, text: str, *, size: int, bold: bool = True) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)


def _add_metadata_table(doc: Document, pop: PopData) -> None:
    table = doc.add_table(rows=2, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [(0, 0, "Código"), (0, 2, "Versão"), (1, 0, "Data"), (1, 2, "Área")]
    for row_idx, col_idx, label in headers:
        style_header_cell(table.rows[row_idx].cells[col_idx], label, shading=SHADING_HEADER)

    table.rows[0].cells[1].text = pop.codigo
    table.rows[0].cells[3].text = pop.versao
    table.rows[1].cells[1].text = pop.data
    table.rows[1].cells[3].text = pop.area


def _add_aviso(doc: Document, aviso: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    run = cell.paragraphs[0].add_run(f"{AVISO_PREFIX}{aviso}")
    run.bold = True
    set_cell_shading(cell, SHADING_AVISO)


def _add_heading(doc: Document, numero: int, texto: str) -> None:
    heading = doc.add_paragraph()
    run = heading.add_run(f"{numero}.  {texto}")
    run.bold = True
    run.font.size = Pt(FONT_HEADING_PT)


def _add_definicoes(doc: Document, pop: PopData, numero: int) -> int:
    if not any(item["termo"].strip() for item in pop.definicoes):
        return numero

    _add_heading(doc, numero, "Definições")
    numero += 1
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    style_header_cell(table.rows[0].cells[0], "Termo", shading=SHADING_HEADER)
    style_header_cell(table.rows[0].cells[1], "Definição", shading=SHADING_HEADER)

    for item in pop.definicoes:
        if item["termo"].strip():
            row = table.add_row()
            row.cells[0].text = item["termo"]
            row.cells[1].text = item["definicao"]
    return numero


def _add_procedimento(doc: Document, pop: PopData, numero: int) -> int:
    for secao in pop.secoes:
        if not secao["titulo"].strip():
            continue

        _add_heading(doc, numero, secao["titulo"])
        numero += 1

        passos_table = doc.add_table(rows=0, cols=2)
        passos_table.style = "Table Grid"
        passos_table.columns[0].width = Cm(PASSO_COL_WIDTH_CM)

        for passo_idx, passo in enumerate(secao["passos"], start=1):
            if passo.strip():
                row = passos_table.add_row()
                row.cells[0].text = str(passo_idx)
                row.cells[1].text = passo
    return numero


def _add_regras(doc: Document, pop: PopData, numero: int) -> int:
    if not any(regra.strip() for regra in pop.regras):
        return numero

    _add_heading(doc, numero, "Regras e Restrições")
    numero += 1
    for regra in pop.regras:
        if regra.strip():
            table = doc.add_table(rows=1, cols=2)
            table.style = "Table Grid"
            table.rows[0].cells[0].text = "R"
            table.rows[0].cells[1].text = regra
    return numero


def _add_consulta(doc: Document, pop: PopData, numero: int) -> int:
    if not pop.consulta:
        return numero

    _add_heading(doc, numero, "Consulta e Relatórios")
    numero += 1
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    table.rows[0].cells[0].text = pop.consulta
    return numero


def _add_revisoes(doc: Document, pop: PopData, numero: int) -> int:
    _add_heading(doc, numero, "Histórico de Revisões")
    numero += 1
    table = doc.add_table(rows=1, cols=4)
    table.style = "Table Grid"

    colunas = ["Revisão", "Data", "Descrição", "Responsável"]
    for idx, titulo in enumerate(colunas):
        style_header_cell(table.rows[0].cells[idx], titulo, shading=SHADING_HEADER)

    for revisao in pop.revisoes:
        if revisao["revisao"].strip():
            row = table.add_row()
            row.cells[0].text = revisao["revisao"]
            row.cells[1].text = revisao["data"]
            row.cells[2].text = revisao["descricao"]
            row.cells[3].text = revisao["responsavel"]
    return numero


def gerar_docx(pop: PopData) -> io.BytesIO:
    doc = Document()
    _configure_margins(doc)

    _add_centered_title(doc, DOCX_TITLE, size=FONT_TITLE_PT)
    _add_centered_title(doc, pop.nome_pop, size=FONT_SUBTITLE_PT)
    doc.add_paragraph()

    _add_metadata_table(doc, pop)
    doc.add_paragraph()

    numero = 1
    _add_heading(doc, numero, "Objetivo")
    numero += 1
    doc.add_paragraph(pop.objetivo)

    _add_heading(doc, numero, "Escopo e Pré-condições")
    numero += 1
    doc.add_paragraph(pop.escopo)
    if pop.aviso:
        _add_aviso(doc, pop.aviso)

    numero = _add_definicoes(doc, pop, numero)
    numero = _add_procedimento(doc, pop, numero)
    numero = _add_regras(doc, pop, numero)
    numero = _add_consulta(doc, pop, numero)
    _add_revisoes(doc, pop, numero)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
