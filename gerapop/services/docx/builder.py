from __future__ import annotations

import io

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from gerapop.constants import (
    COR_SUB,
    DOCX_TITLE,
    FONT_FOOTER_PT,
    FONT_HEADING_PT,
    FONT_SUBTITLE_PT,
    FONT_TITLE_PT,
    MARGIN_BOTTOM_CM,
    MARGIN_LEFT_CM,
    MARGIN_RIGHT_CM,
    MARGIN_TOP_CM,
    SHADING_AVISO,
    SHADING_HEADER,
    SHADING_SUB,
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


def _largura_util_emu(doc: Document) -> int:
    section = doc.sections[0]
    return section.page_width - section.left_margin - section.right_margin


def _larguras_tabela_emu(tabela: Tabela, largura_util: int) -> list[int]:
    if tabela.larguras_cm is None:
        return [largura_util]
    larguras: list[int | None] = [Cm(w).emu if w is not None else None for w in tabela.larguras_cm]
    none_idxs = [i for i, w in enumerate(larguras) if w is None]
    if none_idxs:
        resto = largura_util - sum(w for w in larguras if w is not None)
        base, sobra = divmod(resto, len(none_idxs))
        for k, idx in enumerate(none_idxs):
            larguras[idx] = base + (1 if k < sobra else 0)
        larguras[none_idxs[-1]] += resto - sum(larguras[i] for i in none_idxs)
    return [w for w in larguras if w is not None]


def _segmentos_bold(texto: str) -> list[tuple[str, bool]]:
    partes = texto.split("'")
    if len(partes) % 2 == 0:
        return [(texto, False)]
    return [(parte, idx % 2 == 1) for idx, parte in enumerate(partes) if parte]


def _add_segmentado(paragraph, texto: str, *, bold: bool = False, italic: bool = False) -> None:
    for segmento, em_negrito in _segmentos_bold(texto):
        run = paragraph.add_run(segmento)
        run.bold = bold or em_negrito
        run.italic = italic


def _set_col_widths(table, larguras_emu: list[int]) -> None:
    table.autofit = False
    for idx, width in enumerate(larguras_emu):
        table.columns[idx].width = width
        for cell in table.columns[idx].cells:
            tc_pr = cell._tc.tcPr
            if tc_pr is not None and tc_pr.find(qn("w:gridSpan")) is not None:
                continue
            cell.width = width


def _add_centered_title(doc: Document, text: str, *, size: int) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(size)


def _add_metadata_table(doc: Document, pop: PopData, largura_util: int) -> None:
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

    _set_col_widths(table, [Cm(2.5).emu, Cm(5.5).emu, Cm(2.5).emu, largura_util - Cm(10.5).emu])


def _add_aviso(doc: Document, texto: str, largura_util: int) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    _add_segmentado(cell.paragraphs[0], texto, bold=True)
    set_cell_shading(cell, SHADING_AVISO)
    _set_col_widths(table, [largura_util])


def _add_heading(doc: Document, numero: int, texto: str) -> None:
    heading = doc.add_paragraph()
    run = heading.add_run(f"{numero}.  {texto}")
    run.bold = True
    run.font.size = Pt(FONT_HEADING_PT)


def _add_tabela(doc: Document, tabela: Tabela, largura_util: int) -> None:
    tem_cabecalho = tabela.cabecalho is not None and tabela.com_cabecalho_docx
    colunas = len(tabela.cabecalho) if tabela.cabecalho else len(tabela.linhas[0])
    table = doc.add_table(rows=1 if tem_cabecalho else 0, cols=colunas)
    table.style = "Table Grid"

    if tem_cabecalho:
        for idx, label in enumerate(tabela.cabecalho):
            style_header_cell(table.rows[0].cells[idx], label, shading=SHADING_HEADER)

    estilos = tabela.estilos_linha or tuple("" for _ in tabela.linhas)
    for linha, estilo in zip(tabela.linhas, estilos):
        row = table.add_row()
        if estilo == "sub":
            merged = row.cells[0].merge(row.cells[1])
            run = merged.paragraphs[0].add_run(linha[1])
            run.bold = True
            run.font.color.rgb = RGBColor.from_string(COR_SUB)
            set_cell_shading(merged, SHADING_SUB)
            continue
        for idx, valor in enumerate(linha):
            _add_segmentado(row.cells[idx].paragraphs[0], valor, italic=estilo == "sys")

    _set_col_widths(table, _larguras_tabela_emu(tabela, largura_util))


def _render_blocos(doc: Document, blocos: list[Bloco], largura_util: int) -> None:
    for bloco in blocos:
        if isinstance(bloco, Titulo):
            _add_heading(doc, bloco.numero, bloco.texto)
        elif isinstance(bloco, Paragrafo):
            _add_segmentado(doc.add_paragraph(), bloco.texto, bold=bloco.bold)
        elif isinstance(bloco, Aviso):
            _add_aviso(doc, bloco.texto, largura_util)
        else:
            _add_tabela(doc, bloco, largura_util)


def _add_footer(doc: Document, pop: PopData) -> None:
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False
    paragraph = footer.paragraphs[0]
    largura_util = section.page_width - section.left_margin - section.right_margin
    paragraph.paragraph_format.tab_stops.add_tab_stop(largura_util, WD_TAB_ALIGNMENT.RIGHT)
    run = paragraph.add_run(f"{pop.codigo} · {pop.nome_pop}\tVersão {pop.versao} · Pág. ")
    run.font.size = Pt(FONT_FOOTER_PT)
    run.font.color.rgb = RGBColor(0x5B, 0x66, 0x72)
    campo_pagina = OxmlElement("w:fldSimple")
    campo_pagina.set(qn("w:instr"), "PAGE")
    run_el = OxmlElement("w:r")
    run_props = OxmlElement("w:rPr")
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), str(FONT_FOOTER_PT * 2))
    run_props.append(size)
    run_el.append(run_props)
    t_el = OxmlElement("w:t")
    t_el.text = "1"
    run_el.append(t_el)
    campo_pagina.append(run_el)
    paragraph._p.append(campo_pagina)


def _validar_larguras_tabelas(doc: Document, largura_util: int) -> None:
    for table in doc.tables:
        if not table.rows:
            continue
        primeira = next(
            (
                row
                for row in table.rows
                if not any(
                    (c._tc.tcPr is not None and c._tc.tcPr.find(qn("w:gridSpan")) is not None)
                    for c in row.cells
                )
            ),
            None,
        )
        if primeira is None:
            continue
        widths = [cell.width for cell in primeira.cells]
        if any(w is None for w in widths):
            continue
        soma = sum(widths)
        if soma == largura_util:
            continue
        for cell in table.columns[len(widths) - 1].cells:
            cell.width = widths[-1] + (largura_util - soma)


def gerar_docx(pop: PopData) -> io.BytesIO:
    doc = Document()
    _configure_margins(doc)
    largura_util = _largura_util_emu(doc)

    _add_centered_title(doc, DOCX_TITLE, size=FONT_TITLE_PT)
    _add_centered_title(doc, pop.nome_pop, size=FONT_SUBTITLE_PT)
    doc.add_paragraph()

    _add_metadata_table(doc, pop, largura_util)
    doc.add_paragraph()

    _render_blocos(doc, montar_conteudo(pop), largura_util)
    _validar_larguras_tabelas(doc, largura_util)
    _add_footer(doc, pop)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
