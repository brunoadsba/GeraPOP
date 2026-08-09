"""Constantes compartilhadas do GeraPOP."""

from enum import StrEnum

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
JSON_MIME = "application/json"
DOCX_TITLE = "POP – Procedimento Operacional Padrão"
DATE_FORMAT = "%d/%m/%Y"
DEFAULT_VERSAO = "01"
FILENAME_SLUG_MAX_LEN = 30

# Estilos do documento Word
SHADING_HEADER = "D9D9D9"
SHADING_AVISO = "FFF2CC"
MARGIN_TOP_CM = 2
MARGIN_BOTTOM_CM = 2
MARGIN_LEFT_CM = 2.5
MARGIN_RIGHT_CM = 2.5
FONT_TITLE_PT = 14
FONT_SUBTITLE_PT = 12
FONT_HEADER_PT = 10
PASSO_COL_WIDTH_CM = 1


class SessionKey(StrEnum):
    NOME_POP = "nome_pop"
    CODIGO = "codigo"
    VERSAO = "versao"
    DATA = "data_pop"
    AREA = "area"
    AVISO = "aviso"
    OBJETIVO = "objetivo"
    ESCOPO = "escopo"
    CONSULTA = "consulta"
    DEFINICOES = "definicoes"
    SECOES = "secoes"
    REGRAS = "regras"
    REVISOES = "revisoes"
    GENERATED_POP = "generated_pop"
    GENERATED_DOCX = "generated_docx"
    SAVED_POP_ID = "saved_pop_id"


class ValidationMessage(StrEnum):
    NOME_OBRIGATORIO = "Nome do POP é obrigatório."
    OBJETIVO_OBRIGATORIO = "Objetivo é obrigatório."
    CODIGO_OBRIGATORIO = "Código é obrigatório."
    AREA_OBRIGATORIA = "Área é obrigatória."
