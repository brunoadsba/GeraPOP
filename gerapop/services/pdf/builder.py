"""Geração do POP em PDF — layout padrão oficial CODEBA."""

from __future__ import annotations

import io
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as canvas_module
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from gerapop.constants import (
    COR_SUB,
    DOCX_TITLE,
    FONT_FOOTER_PT,
    FONT_HEADER_PT,
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

MARGIN_TOP_CM = 1.0
MARGIN_BOTTOM_CM = 1.4
MARGIN_LEFT_CM = 1.3
MARGIN_RIGHT_CM = 1.3
_PAGE_W_CM = 21.0 - MARGIN_LEFT_CM - MARGIN_RIGHT_CM  # 18.4 cm

_FONT_DIRS = [
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
    Path("/usr/share/fonts/truetype/calibri"),
    Path("/app/fonts"),
    Path(__file__).resolve().parent.parent.parent / "assets" / "fonts",
]


def _tentar_registrar(nome_ttf: str, arquivo: str) -> str | None:
    """Registra uma fonte TTF (Calibri do padrão CODEBA); None se indisponível."""
    for font_dir in _FONT_DIRS:
        caminho = font_dir / arquivo
        if not caminho.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont(nome_ttf, str(caminho)))
            return nome_ttf
        except Exception:
            continue
    return None


_CANDIDATOS = (
    ("Calibri", "calibri.ttf"),
    ("Calibri-Bold", "calibrib.ttf"),
    ("Calibri-Italic", "calibrii.ttf"),
    ("Calibri-BoldItalic", "calibriz.ttf"),
)
_FONTES = {nome: _tentar_registrar(nome, arq) for nome, arq in _CANDIDATOS}

PDF_REGULAR = _FONTES["Calibri"] or "Helvetica"
PDF_BOLD = _FONTES["Calibri-Bold"] or "Helvetica-Bold"
PDF_ITALIC = _FONTES["Calibri-Italic"] or "Helvetica-Oblique"
PDF_BOLD_ITALIC = _FONTES["Calibri-BoldItalic"] or "Helvetica-BoldOblique"

if PDF_REGULAR == "Calibri":
    pdfmetrics.registerFontFamily(
        "Calibri",
        normal=PDF_REGULAR,
        bold=PDF_BOLD,
        italic=PDF_ITALIC,
        boldItalic=PDF_BOLD_ITALIC,
    )

GRID_COLOR = colors.HexColor("#777777")
HEADER_BG = colors.HexColor(f"#{SHADING_HEADER}")
METADATA_BG = colors.HexColor(f"#{SHADING_METADATA}")
AVISO_BG = colors.HexColor(f"#{SHADING_AVISO}")
SUB_BG = colors.HexColor(f"#{SHADING_SUB}")
SUB_FG = colors.HexColor(f"#{COR_SUB}")
FOOTER_FG = colors.HexColor("#475569")
LINE_COLOR = colors.HexColor("#CBD5E1")
PRIMARY_COLOR = colors.HexColor(f"#{SHADING_HEADER}")

_HEADER_CAT = ParagraphStyle(
    "headercat",
    fontName=PDF_BOLD,
    fontSize=10,
    alignment=TA_RIGHT,
    leading=13,
    textColor=colors.HexColor("#475569"),
)
_HEADER_NAME = ParagraphStyle(
    "headername",
    fontName=PDF_BOLD,
    fontSize=12,
    alignment=TA_RIGHT,
    leading=15,
    textColor=PRIMARY_COLOR,
)
_HEADING = ParagraphStyle(
    "heading",
    fontName=PDF_BOLD,
    fontSize=11,
    leading=14,
    textColor=PRIMARY_COLOR,
    spaceBefore=0.35 * cm,
    spaceAfter=0.12 * cm,
    keepWithNext=True,
)
_SUBHEADING = ParagraphStyle(
    "subheading",
    fontName=PDF_BOLD,
    fontSize=10,
    leading=13,
    textColor=PRIMARY_COLOR,
    spaceBefore=0.25 * cm,
    spaceAfter=0.1 * cm,
    keepWithNext=True,
)
_BODY = ParagraphStyle(
    "body",
    fontName=PDF_REGULAR,
    fontSize=8.5,
    leading=11.5,
    alignment=TA_LEFT,
)
_BODY_BOLD = ParagraphStyle(
    "bodybold",
    parent=_BODY,
    fontName=PDF_BOLD,
)
_CELL = ParagraphStyle(
    "cell",
    fontName=PDF_REGULAR,
    fontSize=8,
    leading=10.5,
)
_CELL_CENTER = ParagraphStyle(
    "cellcenter",
    parent=_CELL,
    alignment=TA_CENTER,
)
_CELL_BOLD = ParagraphStyle(
    "cellbold",
    parent=_CELL,
    fontName=PDF_BOLD,
)
_CELL_BOLD_CENTER = ParagraphStyle(
    "cellboldcenter",
    parent=_CELL_BOLD,
    alignment=TA_CENTER,
)
_CELL_HEADER = ParagraphStyle(
    "cellheader",
    parent=_CELL_BOLD,
    textColor=colors.white,
)
_CELL_HEADER_CENTER = ParagraphStyle(
    "cellheadercenter",
    parent=_CELL_BOLD_CENTER,
    textColor=colors.white,
)
_CELL_ITALIC = ParagraphStyle(
    "cellitalic",
    parent=_CELL,
    fontName=PDF_ITALIC,
)
_CELL_SUB = ParagraphStyle(
    "cellsub",
    parent=_CELL,
    fontName=PDF_BOLD,
    textColor=SUB_FG,
)


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _segmentos_bold_html(texto: str) -> str:
    partes = texto.split("'")
    if len(partes) % 2 == 0:
        return _escape(texto)
    html = ""
    for idx, parte in enumerate(partes):
        if not parte:
            continue
        escaped = _escape(parte)
        html += f"<b>{escaped}</b>" if idx % 2 == 1 else escaped
    return html


def _paragraph(text: str, style: ParagraphStyle = _CELL) -> Paragraph:
    return Paragraph(_segmentos_bold_html(text), style)


def _table(data: list[list], col_widths: list[float], repeat_header: bool = True) -> Table:
    larguras = [w * cm for w in col_widths]
    table = Table(data, colWidths=larguras, repeatRows=1 if repeat_header else 0)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return table


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


def _header_banner(pop: PopData) -> Table:
    logo_path = _obter_logo_path()
    title_p = Paragraph(f"<b>{DOCX_TITLE}</b>", _HEADER_CAT)
    subtitle_p = Paragraph(f"<b>{_escape(pop.nome_pop)}</b>", _HEADER_NAME)

    if logo_path:
        logo_img = RLImage(logo_path, width=4.2 * cm, height=1.18 * cm)
        data = [[logo_img, [title_p, subtitle_p]]]
        table = Table(data, colWidths=[4.2 * cm, (_PAGE_W_CM - 4.2) * cm])
    else:
        data = [[[title_p, subtitle_p]]]
        table = Table(data, colWidths=[_PAGE_W_CM * cm])

    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def _metadata_table(pop: PopData) -> Table:
    """Tabela de metadados (2x4) com estilo oficial CODEBA."""
    data = [
        [
            _paragraph("Código", _CELL_BOLD_CENTER),
            _paragraph(pop.codigo, _CELL_CENTER),
            _paragraph("Versão", _CELL_BOLD_CENTER),
            _paragraph(pop.versao, _CELL_CENTER),
        ],
        [
            _paragraph("Data", _CELL_BOLD_CENTER),
            _paragraph(pop.data, _CELL_CENTER),
            _paragraph("Área", _CELL_BOLD_CENTER),
            _paragraph(pop.area, _CELL),
        ],
    ]
    w_label = 2.82
    w_val1 = 5.67
    w_val2 = 2.82
    w_val3 = 5.20
    table = _table(data, [w_label, w_val1, w_label, w_val3], repeat_header=False)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 1), METADATA_BG),
                ("BACKGROUND", (2, 0), (2, 1), METADATA_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return table


def _revisoes_table(pop: PopData) -> Table:
    """Tabela de histórico de revisões no topo do documento."""
    revisoes = [r for r in pop.revisoes if r.get("revisao", "").strip()]
    if not revisoes:
        revisoes = [default_revisao()]

    data = [
        [
            _paragraph("Rev.", _CELL_HEADER_CENTER),
            _paragraph("Data", _CELL_HEADER_CENTER),
            _paragraph("Histórico de Revisões", _CELL_HEADER),
            _paragraph("Responsável", _CELL_HEADER),
        ]
    ]
    for r in revisoes:
        data.append(
            [
                _paragraph(r.get("revisao", ""), _CELL_CENTER),
                _paragraph(r.get("data", ""), _CELL_CENTER),
                _paragraph(r.get("descricao", "")),
                _paragraph(r.get("responsavel", "")),
            ]
        )

    w_rev = 1.23
    w_dt = 2.47
    w_resp = 3.53
    w_desc = 9.28
    table = _table(data, [w_rev, w_dt, w_desc, w_resp], repeat_header=False)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return table


def _aprovacao_table(pop: PopData) -> Table:
    """Tabela de elaboração e aprovação no topo do documento."""
    data = [
        [
            _paragraph("Elaborado por", _CELL_HEADER),
            _paragraph("Cargo", _CELL_HEADER),
            _paragraph("Aprovado por", _CELL_HEADER),
            _paragraph("Cargo", _CELL_HEADER),
        ],
        [
            _paragraph(pop.elaborado_por or "-"),
            _paragraph(pop.elaborado_cargo or "-"),
            _paragraph(pop.aprovado_por or "[a preencher]"),
            _paragraph(pop.aprovado_cargo or "[a preencher]"),
        ],
    ]
    table = _table(data, [4.94, 3.31, 4.94, 3.31], repeat_header=False)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 2.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
            ]
        )
    )
    return table


def _aviso_table(aviso: str) -> Table:
    conteudo = f"<b>{_escape(aviso)}</b>"
    table = _table([[Paragraph(conteudo, _CELL)]], [_PAGE_W_CM], repeat_header=False)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), AVISO_BG),
                ("TOPPADDING", (0, 0), (-1, -1), 3.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ]
        )
    )
    return table


def _banner_responsavel_table(banner: BannerResponsavel) -> Table:
    bg_color = colors.HexColor(f"#{banner.cor_fundo}")
    fg_color = colors.HexColor(f"#{banner.cor_texto}")
    style = ParagraphStyle(
        "bannerresp",
        parent=_CELL_BOLD,
        textColor=fg_color,
    )
    banner_par = Paragraph(f"<b>{_escape(banner.texto)}</b>", style)
    table = _table([[banner_par]], [_PAGE_W_CM], repeat_header=False)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), bg_color),
                ("TOPPADDING", (0, 0), (-1, -1), 3.0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3.0),
            ]
        )
    )
    return table


def _heading(story: list, numero: int, texto: str) -> None:
    story.append(Paragraph(f"{numero}.  {_escape(texto)}", _HEADING))


def _subheading(story: list, prefixo: str, texto: str) -> None:
    story.append(Paragraph(f"{prefixo} {texto}", _SUBHEADING))


def _larguras_pdf(tabela: Tabela) -> list[float]:
    if tabela.larguras_cm is None:
        return [_PAGE_W_CM]
    definidas = sum(w for w in tabela.larguras_cm if w is not None)
    return [w if w is not None else _PAGE_W_CM - definidas for w in tabela.larguras_cm]


def _tabela_pdf(tabela: Tabela) -> Table:
    data: list[list] = []
    spans: list[tuple[int, int, int]] = []
    if tabela.cabecalho:
        data.append(
            [
                _paragraph(col, _CELL_HEADER_CENTER if col == "#" else _CELL_HEADER)
                for col in tabela.cabecalho
            ]
        )
    estilos = tabela.estilos_linha or tuple("" for _ in tabela.linhas)
    for linha, estilo in zip(tabela.linhas, estilos):
        if estilo == "sub":
            row_idx = len(data)
            data.append([_paragraph(linha[1], _CELL_SUB)])
            spans.append((row_idx, 0, len(linha) - 1))
        elif estilo == "sys":
            data.append([_paragraph(linha[0], _CELL_CENTER), _paragraph(linha[1], _CELL_ITALIC)])
        elif tabela.primeira_celula_bold:
            data.append([_paragraph(linha[0], _CELL_BOLD), *[_paragraph(v) for v in linha[1:]]])
        else:
            if len(linha) >= 2 and linha[0].isdigit():
                data.append(
                    [_paragraph(linha[0], _CELL_CENTER), *[_paragraph(v) for v in linha[1:]]]
                )
            else:
                data.append([_paragraph(v) for v in linha])

    table = _table(data, _larguras_pdf(tabela))
    if tabela.cabecalho:
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (len(tabela.cabecalho) - 1, 0), HEADER_BG),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, 0), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
                ]
            )
        )
    for row_idx, col_start, col_end in spans:
        table.setStyle(
            TableStyle(
                [
                    ("SPAN", (col_start, row_idx), (col_end, row_idx)),
                    ("BACKGROUND", (col_start, row_idx), (col_end, row_idx), SUB_BG),
                    ("TOPPADDING", (col_start, row_idx), (col_end, row_idx), 3),
                    ("BOTTOMPADDING", (col_start, row_idx), (col_end, row_idx), 3),
                ]
            )
        )
    return table


def _render_blocos(story: list, blocos: list[Bloco]) -> None:
    for bloco in blocos:
        if isinstance(bloco, Titulo):
            _heading(story, bloco.numero, bloco.texto)
        elif isinstance(bloco, Subtitulo):
            _subheading(story, bloco.prefixo, bloco.texto)
        elif isinstance(bloco, BannerResponsavel):
            story.append(_banner_responsavel_table(bloco))
            story.append(Spacer(1, 0.1 * cm))
        elif isinstance(bloco, Paragrafo):
            style = _BODY_BOLD if bloco.bold else _BODY
            story.append(Paragraph(_segmentos_bold_html(bloco.texto), style))
        elif isinstance(bloco, Aviso):
            story.append(_aviso_table(bloco.texto))
            story.append(Spacer(1, 0.1 * cm))
        else:
            story.append(_tabela_pdf(bloco))
            story.append(Spacer(1, 0.15 * cm))


class _NumberedCanvas(canvas_module.Canvas):
    """Canvas que conhece o total de páginas para desenhar "Página X de Y".

    O cabeçalho de rodapé oficial CODEBA é desenhado no `save()` em uma segunda
    passagem, quando o número total de páginas já é conhecido.
    """

    def __init__(self, *args, pop: PopData, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict] = []
        self._pop = pop

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._desenhar_cabecalho_rodape(total_pages)
            super().showPage()
        super().save()

    def _desenhar_cabecalho_rodape(self, total_pages: int) -> None:
        pop = self._pop
        page_num = self._pageNumber
        nome_titulo = titulo_para_header(pop.nome_pop)

        # Linha divisória acima do rodapé
        self.setStrokeColor(LINE_COLOR)
        self.setLineWidth(0.5)
        self.line(
            MARGIN_LEFT_CM * cm,
            1.2 * cm,
            A4[0] - MARGIN_RIGHT_CM * cm,
            1.2 * cm,
        )

        # Rodapé (todas as páginas): "COD – Nome · Versão    Página X de Y"
        self.setFont(PDF_REGULAR, FONT_FOOTER_PT)
        self.setFillColor(FOOTER_FG)
        self.drawString(
            MARGIN_LEFT_CM * cm,
            0.8 * cm,
            f"{pop.codigo} – {nome_titulo} · Versão {pop.versao}",
        )
        self.drawRightString(
            A4[0] - MARGIN_RIGHT_CM * cm,
            0.8 * cm,
            f"Página {page_num} de {total_pages}",
        )

        self.setFont(PDF_ITALIC, 7)
        self.setFillColor(colors.HexColor("#94A3B8"))
        self.drawCentredString(
            A4[0] / 2.0,
            0.35 * cm,
            "Documento impresso é uma CÓPIA NÃO CONTROLADA — verifique a versão vigente "
            "no controle de documentos antes de utilizá-la.",
        )

        # Cabeçalho corrente a partir da página 2 (a página 1 tem o banner)
        if page_num > 1:
            self.setFont(PDF_REGULAR, FONT_HEADER_PT)
            self.setFillColor(colors.HexColor("#718096"))
            self.drawRightString(
                A4[0] - MARGIN_RIGHT_CM * cm,
                A4[1] - MARGIN_TOP_CM * cm + 0.55 * cm,
                f"{pop.codigo} · {nome_titulo} · Versão {pop.versao} · "
                f"Página {page_num} de {total_pages}",
            )


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

    # 1. Cabeçalho com Logo CODEBA à esquerda + Título do POP
    story.append(_header_banner(pop))
    story.append(Spacer(1, 0.15 * cm))

    # 2. Tabela de Metadados (2x4)
    story.append(_metadata_table(pop))
    story.append(Spacer(1, 0.15 * cm))

    # 3. Histórico de Revisões no Topo
    story.append(_revisoes_table(pop))
    story.append(Spacer(1, 0.15 * cm))

    # 4. Elaboração e Aprovação no Topo
    story.append(_aprovacao_table(pop))
    story.append(Spacer(1, 0.2 * cm))

    # 5. Seções numeradas do documento
    _render_blocos(story, montar_conteudo(pop))

    doc.build(story, canvasmaker=lambda *args, **kwargs: _NumberedCanvas(*args, pop=pop, **kwargs))
    buffer.seek(0)
    return buffer
