"""GeraPOP — gerador de POP (Procedimento Operacional Padrão) CODEBA."""

from gerapop.models import PopData
from gerapop.services.docx import gerar_docx

__all__ = ["PopData", "gerar_docx"]
__version__ = "0.1.0"
