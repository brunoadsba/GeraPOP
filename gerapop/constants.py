"""Constantes compartilhadas do GeraPOP."""

from enum import StrEnum

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
PDF_MIME = "application/pdf"
DOCX_TITLE = "POP – Procedimento Operacional Padrão"
DATE_FORMAT = "%d/%m/%Y"
DEFAULT_VERSAO = "01"
FILENAME_SLUG_MAX_LEN = 30

# Estilos do documento Word
SHADING_HEADER = "D9D9D9"
SHADING_AVISO = "FFF2CC"
SHADING_SUB = "EAF1F6"
COR_SUB = "0B3954"
MARGIN_TOP_CM = 2
MARGIN_BOTTOM_CM = 2
MARGIN_LEFT_CM = 2.5
MARGIN_RIGHT_CM = 2.5
FONT_TITLE_PT = 18
FONT_SUBTITLE_PT = 13
FONT_HEADING_PT = 13
FONT_HEADER_PT = 10
FONT_FOOTER_PT = 8
PASSO_COL_WIDTH_CM = 1

AVISO_PREFIX = "⚠ ATENÇÃO: "
SUB_PREFIXO = "Tela "
SISTEMA_PREFIXO = "Sistema "


class ValidationMessage(StrEnum):
    NOME_OBRIGATORIO = "Nome do POP é obrigatório."
    OBJETIVO_OBRIGATORIO = "Objetivo é obrigatório."
    CODIGO_OBRIGATORIO = "Código é obrigatório."
    AREA_OBRIGATORIA = "Área é obrigatória."
