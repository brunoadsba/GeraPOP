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
    AVISO_PREFIX,
    DOCX_TITLE,
    FONT_HEADER_PT,
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
    conteudo = f"<b>{_escape(AVISO_PREFIX + aviso)}</b>"
    table = _table([[Paragraph(conteudo, _CELL)]], [_PAGE_W_CM])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), AVISO_BG)]))
    return table


def _heading(story: list, numero: int, texto: str) -> int:
    story.append(Paragraph(f"{numero}.  {_escape(texto)}", _HEADING))
    return numero + 1


def _add_definicoes(story: list, pop: PopData, numero: int) -> int:
    if not any(item["termo"].strip() for item in pop.definicoes):
        return numero
    numero = _heading(story, numero, "Definições")
    data = [[_paragraph("Termo", _CELL_BOLD), _paragraph("Definição", _CELL_BOLD)]]
    for item in pop.definicoes:
        if item["termo"].strip():
            data.append([_paragraph(item["termo"]), _paragraph(item["definicao"])])
    table = _table(data, [4.5, _PAGE_W_CM - 4.5])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (1, 0), HEADER_BG)]))
    story.append(table)
    return numero


def _add_procedimento(story: list, pop: PopData, numero: int) -> int:
    for secao in pop.secoes:
        if not secao["titulo"].strip():
            continue
        numero = _heading(story, numero, secao["titulo"])

        data = [[_paragraph("#", _CELL_BOLD), _paragraph("Passo", _CELL_BOLD)]]
        for passo_idx, passo in enumerate(secao["passos"], start=1):
            if passo.strip():
                data.append([_paragraph(str(passo_idx)), _paragraph(passo)])
        passos_table = _table(data, [PASSO_COL_WIDTH_CM, _PAGE_W_CM - PASSO_COL_WIDTH_CM])
        passos_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (1, 0), HEADER_BG)]))
        story.append(passos_table)

        campos = secao.get("campos", [])
        if any(item["campo"].strip() for item in campos):
            titulo = _escape(secao["titulo"])
            story.append(Paragraph(f"<b>Campos obrigatórios – {titulo}:</b>", _BODY))
            data = [
                [_paragraph("Campo", _CELL_BOLD), _paragraph("Descrição / Instruções", _CELL_BOLD)]
            ]
            for item in campos:
                if item["campo"].strip():
                    data.append([_paragraph(item["campo"]), _paragraph(item["descricao"])])
            campos_table = _table(data, [4.5, _PAGE_W_CM - 4.5])
            campos_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (1, 0), HEADER_BG)]))
            story.append(campos_table)
    return numero


def _add_regras(story: list, pop: PopData, numero: int) -> int:
    if not any(regra.strip() for regra in pop.regras):
        return numero
    numero = _heading(story, numero, "Regras e Restrições")
    for regra in pop.regras:
        if regra.strip():
            story.append(
                _table([[_paragraph("R", _CELL_BOLD), _paragraph(regra)]], [1.5, _PAGE_W_CM - 1.5])
            )
    return numero


def _add_consulta(story: list, pop: PopData, numero: int) -> int:
    if not pop.consulta:
        return numero
    numero = _heading(story, numero, "Consulta e Relatórios")
    story.append(_table([[_paragraph(pop.consulta)]], [_PAGE_W_CM]))
    return numero


def _add_revisoes(story: list, pop: PopData, numero: int) -> int:
    numero = _heading(story, numero, "Histórico de Revisões")
    data = [
        [_paragraph(col, _CELL_BOLD) for col in ("Revisão", "Data", "Descrição", "Responsável")]
    ]
    for revisao in pop.revisoes:
        if revisao["revisao"].strip():
            data.append(
                [
                    _paragraph(revisao["revisao"]),
                    _paragraph(revisao["data"]),
                    _paragraph(revisao["descricao"]),
                    _paragraph(revisao["responsavel"]),
                ]
            )
    table = _table(data, [1.8, 2.4, _PAGE_W_CM - 7.2, 3.0])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (3, 0), HEADER_BG)]))
    story.append(table)
    return numero


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

    numero = 1
    numero = _heading(story, numero, "Objetivo")
    story.append(Paragraph(_escape(pop.objetivo), _BODY))

    numero = _heading(story, numero, "Escopo e Pré-condições")
    story.append(Paragraph(_escape(pop.escopo), _BODY))
    if pop.aviso:
        story.append(_aviso_table(pop.aviso))

    numero = _add_definicoes(story, pop, numero)
    numero = _add_procedimento(story, pop, numero)
    numero = _add_regras(story, pop, numero)
    numero = _add_consulta(story, pop, numero)
    _add_revisoes(story, pop, numero)

    doc.build(story)
    buffer.seek(0)
    return buffer
