"""Seções do formulário POP — API pública do pacote `ui.form`."""

from gerapop.ui.form.conteudo import (
    ConteudoFields,
    build_pop,
    render_consulta,
    render_objetivo_escopo,
    try_generate,
)
from gerapop.ui.form.dinamicas import (
    render_definicoes,
    render_procedimento,
    render_regras,
    render_revisoes,
)
from gerapop.ui.form.identificacao import IdentificacaoFields, render_identificacao
from gerapop.ui.form.widgets import render_header

__all__ = [
    "ConteudoFields",
    "IdentificacaoFields",
    "build_pop",
    "render_consulta",
    "render_definicoes",
    "render_header",
    "render_identificacao",
    "render_objetivo_escopo",
    "render_procedimento",
    "render_regras",
    "render_revisoes",
    "try_generate",
]
