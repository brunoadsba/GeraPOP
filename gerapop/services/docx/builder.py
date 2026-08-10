from __future__ import annotations

import io

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

from gerapop.constants import (
    DOCX_TITLE,
    FONT_HEADING_PT,
    FONT_SUBTITLE_PT,
    FONT_TITLE_PT,
    MARGIN_BOTTOM_CM,
    MARGIN_LEFT_CM,
    MARGIN_RIGHT_CM,
    MARGIN_TOP_CM,
    SHADING_AVISO,
    SHADING_HEADER,
)
from gerapop.models import PopData
from gerapop.services.documento import Aviso, Bloco, Paragrafo, Tabela, Titulo, montar_conteudo
from gerapop.services.docx.styles import set_cell_shading, style_header_cell


def _configure_margins(doc: Document) -> None:
    for section in doc.sections:
        section.top_margin = Cm(MARGIN_TOP_CM)
        section.bottom_margin = Cm(MARGIN_BOTTOM_CM)
        section.left_margin = Cm(MARGIN_LEFT_CM)
        section.right_margin = Cm(MARGIN_RIGHT_CM)


def _add_centered_title(doc: Document, text: str, *, size: int) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = True
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


def _add_aviso(doc: Document, texto: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    run = cell.paragraphs[0].add_run(texto)
    run.bold = True
    set_cell_shading(cell, SHADING_AVISO)


def _add_heading(doc: Document, numero: int, texto: str) -> None:
    heading = doc.add_paragraph()
    run = heading.add_run(f"{numero}.  {texto}")
    run.bold = True
    run.font.size = Pt(FONT_HEADING_PT)


def _add_tabela(doc: Document, tabela: Tabela) -> None:
    tem_cabecalho = tabela.cabecalho is not None and tabela.com_cabecalho_docx
    colunas = len(tabela.cabecalho) if tabela.cabecalho else len(tabela.linhas[0])
    table = doc.add_table(rows=1 if tem_cabecalho else 0, cols=colunas)
    table.style = "Table Grid"

    if tabela.largura_col0_docx_cm is not None:
        table.columns[0].width = Cm(tabela.largura_col0_docx_cm)

    if tem_cabecalho:
        for idx, label in enumerate(tabela.cabecalho):
            style_header_cell(table.rows[0].cells[idx], label, shading=SHADING_HEADER)

    for linha in tabela.linhas:
        row = table.add_row()
        for idx, valor in enumerate(linha):
            row.cells[idx].text = valor


def _render_blocos(doc: Document, blocos: list[Bloco]) -> None:
    for bloco in blocos:
        if isinstance(bloco, Titulo):
            _add_heading(doc, bloco.numero, bloco.texto)
        elif isinstance(bloco, Paragrafo):
            run = doc.add_paragraph().add_run(bloco.texto)
            run.bold = bloco.bold
        elif isinstance(bloco, Aviso):
            _add_aviso(doc, bloco.texto)
        else:
            _add_tabela(doc, bloco)


def gerar_docx(pop: PopData) -> io.BytesIO:
    doc = Document()
    _configure_margins(doc)

    _add_centered_title(doc, DOCX_TITLE, size=FONT_TITLE_PT)
    _add_centered_title(doc, pop.nome_pop, size=FONT_SUBTITLE_PT)
    doc.add_paragraph()

    _add_metadata_table(doc, pop)
    doc.add_paragraph()

    _render_blocos(doc, montar_conteudo(pop))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
