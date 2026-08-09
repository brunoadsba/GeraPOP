"""Estilos reutilizáveis para células e parágrafos do Word."""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from gerapop.constants import FONT_HEADER_PT


def set_cell_shading(cell, color_hex: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:val"), "clear")
    shading.set(qn("w:color"), "auto")
    shading.set(qn("w:fill"), color_hex)
    tc_pr.append(shading)


def style_header_cell(
    cell,
    text: str,
    *,
    bold: bool = True,
    size: int = FONT_HEADER_PT,
    shading: str | None = None,
    color: tuple[int, int, int] | None = None,
) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)
    if shading:
        set_cell_shading(cell, shading)
