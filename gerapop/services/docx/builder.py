from __future__ import annotations

import io
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.text.paragraph import Paragraph

from gerapop.constants import (
    COR_SUB,
    FONT_FOOTER_PT,
    FONT_HEADER_PT,
    FONT_HEADING_PT,
    FONT_SUBHEADING_PT,
    MARGIN_BOTTOM_CM,
    MARGIN_LEFT_CM,
    MARGIN_RIGHT_CM,
    MARGIN_TOP_CM,
    SHADING_AVISO,
    SHADING_HEADER,
    SHADING_METADATA,
    SHADING_SUB,
)
from gerapop.models import PopData, default_revisao
from gerapop.services.documento import (
    Aviso,
    BannerResponsavel,
    Bloco,
    Paragrafo,
    Subtitulo,
    Tabela,
    Titulo,
    montar_conteudo,
    titulo_para_header,
)
from gerapop.services.docx.styles import set_cell_shading, style_header_cell

PRIMARY_COLOR_RGB = (0x1F, 0x4E, 0x79)


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
        if idx < len(table.columns):
            table.columns[idx].width = width
            for cell in table.columns[idx].cells:
                tc_pr = cell._tc.tcPr
                if tc_pr is not None and tc_pr.find(qn("w:gridSpan")) is not None:
                    continue
                cell.width = width


def _obter_logo_path() -> str | None:
    raiz = Path(__file__).resolve().parent.parent.parent.parent
    candidatos = [
        raiz / "frontend" / "public" / "logo-codeba-topo.png",
        raiz / "gerapop" / "assets" / "logo-codeba.png",
        raiz / "Logo CODEBA.png",
        Path("Logo CODEBA.png"),
    ]
    for c in candidatos:
        if c.is_file():
            return str(c)
    return None


def _add_header_banner(doc: Document, pop: PopData, largura_util: int) -> None:
    logo_path = _obter_logo_path()
    table = doc.add_table(rows=1, cols=2 if logo_path else 1)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Remove bordas da tabela do banner
    tblPr = table._tbl.tblPr
    tblBorders = tblPr.find(qn("w:tblBorders"))
    if tblBorders is None:
        tblBorders = OxmlElement("w:tblBorders")
        tblPr.append(tblBorders)
    for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{border_name}")
        b.set(qn("w:val"), "none")
        tblBorders.append(b)

    if logo_path:
        cell_logo = table.rows[0].cells[0]
        p_logo = cell_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Cm(3.88))

        cell_title = table.rows[0].cells[1]
        p_title = cell_title.paragraphs[0]
        p_title.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run_cat = p_title.add_run("POP – Procedimento Operacional Padrão\n")
        run_cat.font.size = Pt(11)
        run_cat.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
        run_name = p_title.add_run(pop.nome_pop)
        run_name.bold = True
        run_name.font.size = Pt(13)
        run_name.font.color.rgb = RGBColor(*PRIMARY_COLOR_RGB)

        w_logo = Cm(4.2).emu
        _set_col_widths(table, [w_logo, largura_util - w_logo])
    else:
        cell_title = table.rows[0].cells[0]
        p_title = cell_title.paragraphs[0]
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cat = p_title.add_run("POP – Procedimento Operacional Padrão\n")
        run_cat.font.size = Pt(11)
        run_name = p_title.add_run(pop.nome_pop)
        run_name.bold = True
        run_name.font.size = Pt(14)
        run_name.font.color.rgb = RGBColor(*PRIMARY_COLOR_RGB)
        _set_col_widths(table, [largura_util])

    doc.add_paragraph()


def _add_metadata_table(doc: Document, pop: PopData, largura_util: int) -> None:
    table = doc.add_table(rows=2, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [(0, 0, "Código"), (0, 2, "Versão"), (1, 0, "Data"), (1, 2, "Área")]
    for row_idx, col_idx, label in headers:
        style_header_cell(
            table.rows[row_idx].cells[col_idx],
            label,
            shading=SHADING_METADATA,
            color=(0x1E, 0x29, 0x3B),
            size=9,
        )

    table.rows[0].cells[1].text = pop.codigo
    table.rows[0].cells[3].text = pop.versao
    table.rows[1].cells[1].text = pop.data
    table.rows[1].cells[3].text = pop.area

    # Larguras equilibradas (15.92 cm útil total em margem 2.54)
    w_label = Cm(2.82).emu
    w_cod = Cm(5.67).emu
    w_area = largura_util - (w_label * 2 + w_cod)
    _set_col_widths(table, [w_label, w_cod, w_label, w_area])
    doc.add_paragraph()


def _add_revisoes_table(doc: Document, pop: PopData, largura_util: int) -> None:
    revisoes = [r for r in pop.revisoes if r.get("revisao", "").strip()]
    if not revisoes:
        revisoes = [default_revisao()]

    table = doc.add_table(rows=1 + len(revisoes), cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Rev.", "Data", "Histórico de Revisões", "Responsável"]
    for idx, label in enumerate(headers):
        style_header_cell(
            table.rows[0].cells[idx],
            label,
            shading=SHADING_HEADER,
            color=(0xFF, 0xFF, 0xFF),
            size=9,
        )

    for r_idx, rev in enumerate(revisoes, start=1):
        table.rows[r_idx].cells[0].text = rev.get("revisao", "")
        table.rows[r_idx].cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        table.rows[r_idx].cells[1].text = rev.get("data", "")
        table.rows[r_idx].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        table.rows[r_idx].cells[2].text = rev.get("descricao", "")
        table.rows[r_idx].cells[3].text = rev.get("responsavel", "")

    w_rev = Cm(1.23).emu
    w_dt = Cm(2.47).emu
    w_resp = Cm(3.53).emu
    w_desc = largura_util - (w_rev + w_dt + w_resp)
    _set_col_widths(table, [w_rev, w_dt, w_desc, w_resp])
    doc.add_paragraph()


def _add_aprovacao_table(doc: Document, pop: PopData, largura_util: int) -> None:
    table = doc.add_table(rows=2, cols=4)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = ["Elaborado por", "Cargo", "Aprovado por", "Cargo"]
    for idx, label in enumerate(headers):
        style_header_cell(
            table.rows[0].cells[idx],
            label,
            shading=SHADING_HEADER,
            color=(0xFF, 0xFF, 0xFF),
            size=9,
        )

    table.rows[1].cells[0].text = pop.elaborado_por or "-"
    table.rows[1].cells[1].text = pop.elaborado_cargo or "-"
    table.rows[1].cells[2].text = pop.aprovado_por or "[a preencher]"
    table.rows[1].cells[3].text = pop.aprovado_cargo or "[a preencher]"

    w_nome = Cm(4.94).emu
    w_cargo = (largura_util - (w_nome * 2)) // 2
    _set_col_widths(table, [w_nome, w_cargo, w_nome, largura_util - (w_nome * 2 + w_cargo)])
    doc.add_paragraph()


def _add_aviso(doc: Document, texto: str, largura_util: int) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    _add_segmentado(cell.paragraphs[0], texto, bold=True)
    set_cell_shading(cell, SHADING_AVISO)
    _set_col_widths(table, [largura_util])
    doc.add_paragraph()


def _add_banner_responsavel(doc: Document, banner: BannerResponsavel, largura_util: int) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.rows[0].cells[0]
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(banner.texto)
    run.bold = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor.from_string(banner.cor_texto)
    set_cell_shading(cell, banner.cor_fundo)
    _set_col_widths(table, [largura_util])


def _add_heading(doc: Document, numero: int, texto: str) -> None:
    heading = doc.add_paragraph()
    heading.paragraph_format.space_before = Pt(8)
    heading.paragraph_format.space_after = Pt(3)
    heading.paragraph_format.keep_with_next = True
    run = heading.add_run(f"{numero}.  {texto}")
    run.bold = True
    run.font.size = Pt(FONT_HEADING_PT)
    run.font.color.rgb = RGBColor(*PRIMARY_COLOR_RGB)


def _add_subheading(doc: Document, prefixo: str, texto: str) -> None:
    heading = doc.add_paragraph()
    heading.paragraph_format.space_before = Pt(6)
    heading.paragraph_format.space_after = Pt(2)
    heading.paragraph_format.keep_with_next = True
    run = heading.add_run(f"{prefixo} {texto}")
    run.bold = True
    run.font.size = Pt(FONT_SUBHEADING_PT)
    run.font.color.rgb = RGBColor(*PRIMARY_COLOR_RGB)


def _add_tabela(doc: Document, tabela: Tabela, largura_util: int) -> None:
    tem_cabecalho = tabela.cabecalho is not None and tabela.com_cabecalho_docx
    linha_exemplo = tabela.linhas[0] if tabela.linhas else []
    if tabela.cabecalho:
        colunas = len(tabela.cabecalho)
    else:
        colunas = len(linha_exemplo) if linha_exemplo else 1
    table = doc.add_table(rows=1 if tem_cabecalho else 0, cols=colunas)
    table.style = "Table Grid"

    if tem_cabecalho and tabela.cabecalho:
        for idx, label in enumerate(tabela.cabecalho):
            style_header_cell(
                table.rows[0].cells[idx],
                label,
                shading=SHADING_HEADER,
                color=(0xFF, 0xFF, 0xFF),
                size=9,
            )

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
            p = row.cells[idx].paragraphs[0]
            # Se for coluna de número (#) ou estilo sys/primeira célula
            if idx == 0 and len(linha) >= 2 and valor.isdigit():
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(valor)
                run.bold = True
            elif idx == 0 and tabela.primeira_celula_bold:
                _add_segmentado(p, valor, bold=True, italic=estilo == "sys")
            else:
                _add_segmentado(p, valor, italic=estilo == "sys")

    _set_col_widths(table, _larguras_tabela_emu(tabela, largura_util))
    doc.add_paragraph()


def _render_blocos(doc: Document, blocos: list[Bloco], largura_util: int) -> None:
    for bloco in blocos:
        if isinstance(bloco, Titulo):
            _add_heading(doc, bloco.numero, bloco.texto)
        elif isinstance(bloco, Subtitulo):
            _add_subheading(doc, bloco.prefixo, bloco.texto)
        elif isinstance(bloco, BannerResponsavel):
            _add_banner_responsavel(doc, bloco, largura_util)
        elif isinstance(bloco, Paragrafo):
            p = doc.add_paragraph()
            _add_segmentado(p, bloco.texto, bold=bloco.bold)
        elif isinstance(bloco, Aviso):
            _add_aviso(doc, bloco.texto, largura_util)
        else:
            _add_tabela(doc, bloco, largura_util)


def _add_pagina_campos(p: Paragraph, *, de: bool = True, tamanho: float = FONT_FOOTER_PT) -> None:
    """Insere os campos de página "Página X de Y" (PAGE e NUMPAGES)."""
    for instr, default in (("PAGE", "1"), ("NUMPAGES", "1")):
        campo = OxmlElement("w:fldSimple")
        campo.set(qn("w:instr"), instr)
        run = OxmlElement("w:r")
        run_props = OxmlElement("w:rPr")
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(round(tamanho * 2)))
        run_props.append(sz)
        run.append(run_props)
        t = OxmlElement("w:t")
        t.text = default
        run.append(t)
        campo.append(run)
        p._p.append(campo)


def _add_header_footer(doc: Document, pop: PopData) -> None:
    section = doc.sections[0]
    largura_util = section.page_width - section.left_margin - section.right_margin
    nome_titulo = titulo_para_header(pop.nome_pop)

    # Header somente a partir da página 2 (página 1 tem o banner institucional)
    section.different_first_page_header_footer = True

    header = section.header
    header.is_linked_to_previous = False
    p_hdr = header.paragraphs[0]
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run_hdr = p_hdr.add_run(f"{pop.codigo} · {nome_titulo} · Versão {pop.versao} · Página ")
    run_hdr.font.size = Pt(FONT_HEADER_PT)
    run_hdr.font.color.rgb = RGBColor(0x71, 0x80, 0x96)
    _add_pagina_campos(p_hdr, de=True, tamanho=FONT_HEADER_PT)

    # Footer
    footer = section.footer
    footer.is_linked_to_previous = False
    p_ftr = footer.paragraphs[0]
    p_ftr.paragraph_format.tab_stops.add_tab_stop(largura_util, WD_TAB_ALIGNMENT.RIGHT)
    run_ftr_l = p_ftr.add_run(f"{pop.codigo} – {nome_titulo} · Versão {pop.versao}\tPágina ")
    run_ftr_l.font.size = Pt(FONT_FOOTER_PT)
    run_ftr_l.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
    _add_pagina_campos(p_ftr, de=True, tamanho=FONT_FOOTER_PT)

    # Linha 2 de aviso cópia não controlada
    p_aviso = footer.add_paragraph()
    p_aviso.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_aviso = p_aviso.add_run(
        "Documento impresso é uma CÓPIA NÃO CONTROLADA — verifique a versão vigente no controle de "
        "documentos antes de utilizá-la."
    )
    run_aviso.font.size = Pt(7.5)
    run_aviso.italic = True
    run_aviso.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)


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

    # 1. Topo: Banner (Logo + Título)
    _add_header_banner(doc, pop, largura_util)

    # 2. Topo: Metadados (2x4)
    _add_metadata_table(doc, pop, largura_util)

    # 3. Topo: Histórico de Revisões
    _add_revisoes_table(doc, pop, largura_util)

    # 4. Topo: Elaboração e Aprovação
    _add_aprovacao_table(doc, pop, largura_util)

    # 5. Seções Numeradas do Procedimento
    _render_blocos(doc, montar_conteudo(pop), largura_util)

    _validar_larguras_tabelas(doc, largura_util)
    _add_header_footer(doc, pop)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
