"""Geração do POP em PDF — mesma estrutura do builder .docx."""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from gerapop.constants import (
    DOCX_TITLE,
    FONT_HEADER_PT,
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

GRID_COLOR = colors.HexColor("#666666")
HEADER_BG = colors.HexColor(f"#{SHADING_HEADER}")
AVISO_BG = colors.HexColor(f"#{SHADING_AVISO}")

_PAGE_W_CM = 21.0 - MARGIN_LEFT_CM - MARGIN_RIGHT_CM

_TITLE = ParagraphStyle(
    "titulo",
    fontName="Helvetica-Bold",
    fontSize=FONT_TITLE_PT,
    alignment=TA_CENTER,
    leading=FONT_TITLE_PT * 1.25,
)
_SUBTITLE = ParagraphStyle(
    "subtitulo",
    fontName="Helvetica-Bold",
    fontSize=FONT_SUBTITLE_PT,
    alignment=TA_CENTER,
    leading=FONT_SUBTITLE_PT * 1.25,
    spaceAfter=0.4 * cm,
)
_HEADING = ParagraphStyle(
    "heading",
    fontName="Helvetica-Bold",
    fontSize=FONT_HEADING_PT,
    leading=FONT_HEADING_PT * 1.25,
    spaceBefore=0.35 * cm,
    spaceAfter=0.15 * cm,
)
_BODY = ParagraphStyle(
    "body",
    fontName="Helvetica",
    fontSize=FONT_HEADER_PT,
    leading=FONT_HEADER_PT * 1.4,
)
_BODY_BOLD = ParagraphStyle(
    "bodybold",
    parent=_BODY,
    fontName="Helvetica-Bold",
)
_CELL = ParagraphStyle(
    "cell",
    fontName="Helvetica",
    fontSize=FONT_HEADER_PT,
    leading=FONT_HEADER_PT * 1.35,
)
_CELL_BOLD = ParagraphStyle(
    "cellbold",
    parent=_CELL,
    fontName="Helvetica-Bold",
)


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraph(text: str, style: ParagraphStyle = _CELL) -> Paragraph:
    return Paragraph(_escape(text), style)


def _table(data: list[list], col_widths: list[float]) -> Table:
    table = Table(data, colWidths=[w * cm for w in col_widths], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _metadata_table(pop: PopData) -> Table:
    data = [
        [
            _paragraph("Código", _CELL_BOLD),
            _paragraph(pop.codigo),
            _paragraph("Versão", _CELL_BOLD),
            _paragraph(pop.versao),
        ],
        [
            _paragraph("Data", _CELL_BOLD),
            _paragraph(pop.data),
            _paragraph("Área", _CELL_BOLD),
            _paragraph(pop.area),
        ],
    ]
    table = _table(data, [2.5, 5.5, 2.5, _PAGE_W_CM - 10.5])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), HEADER_BG),
                ("BACKGROUND", (2, 0), (2, 0), HEADER_BG),
                ("BACKGROUND", (0, 1), (0, 1), HEADER_BG),
                ("BACKGROUND", (2, 1), (2, 1), HEADER_BG),
            ]
        )
    )
    return table


def _aviso_table(aviso: str) -> Table:
    conteudo = f"<b>{_escape(aviso)}</b>"
    table = _table([[Paragraph(conteudo, _CELL)]], [_PAGE_W_CM])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), AVISO_BG)]))
    return table


def _heading(story: list, numero: int, texto: str) -> None:
    story.append(Paragraph(f"{numero}.  {_escape(texto)}", _HEADING))


def _larguras_pdf(tabela: Tabela) -> list[float]:
    if tabela.larguras_cm is None:
        return [_PAGE_W_CM]
    definidas = sum(w for w in tabela.larguras_cm if w is not None)
    return [w if w is not None else _PAGE_W_CM - definidas for w in tabela.larguras_cm]


def _tabela_pdf(tabela: Tabela) -> Table:
    data: list[list] = []
    if tabela.cabecalho:
        data.append([_paragraph(col, _CELL_BOLD) for col in tabela.cabecalho])
    for linha in tabela.linhas:
        if tabela.primeira_celula_bold:
            data.append([_paragraph(linha[0], _CELL_BOLD), *[_paragraph(v) for v in linha[1:]]])
        else:
            data.append([_paragraph(v) for v in linha])

    table = _table(data, _larguras_pdf(tabela))
    if tabela.cabecalho:
        table.setStyle(
            TableStyle([("BACKGROUND", (0, 0), (len(tabela.cabecalho) - 1, 0), HEADER_BG)])
        )
    return table


def _render_blocos(story: list, blocos: list[Bloco]) -> None:
    for bloco in blocos:
        if isinstance(bloco, Titulo):
            _heading(story, bloco.numero, bloco.texto)
        elif isinstance(bloco, Paragrafo):
            style = _BODY_BOLD if bloco.bold else _BODY
            story.append(Paragraph(_escape(bloco.texto), style))
        elif isinstance(bloco, Aviso):
            story.append(_aviso_table(bloco.texto))
        else:
            story.append(_tabela_pdf(bloco))


def gerar_pdf(pop: PopData) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=MARGIN_TOP_CM * cm,
        bottomMargin=MARGIN_BOTTOM_CM * cm,
        leftMargin=MARGIN_LEFT_CM * cm,
        rightMargin=MARGIN_RIGHT_CM * cm,
        title=f"{DOCX_TITLE} — {pop.nome_pop}",
        author="GeraPOP CODEBA",
    )
    story: list = []
    story.append(Paragraph(DOCX_TITLE, _TITLE))
    story.append(Paragraph(pop.nome_pop, _SUBTITLE))

    story.append(_metadata_table(pop))
    story.append(Spacer(1, 0.25 * cm))

    _render_blocos(story, montar_conteudo(pop))

    doc.build(story)
    buffer.seek(0)
    return buffer
