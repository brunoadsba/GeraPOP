from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import TypedDict

from gerapop.constants import (
    DATE_FORMAT,
    DEFAULT_VERSAO,
    FILENAME_SLUG_MAX_LEN,
    ValidationMessage,
)


class Definicao(TypedDict):
    termo: str
    definicao: str


class CampoProcedimento(TypedDict):
    campo: str
    descricao: str


class ItemMatriz(TypedDict):
    tela: str
    nome_tela: str
    etapa: str
    responsavel: str


class Secao(TypedDict):
    titulo: str
    responsavel: str  # ex: "OPERADOR PORTUÁRIO (PRESTADOR)" ou "TPO CONTROLE"
    passos: list[str]
    campos: list[CampoProcedimento]  # opcional (dados antigos podem não ter)


class Revisao(TypedDict):
    revisao: str
    data: str
    descricao: str
    responsavel: str


def default_definicao() -> Definicao:
    return {"termo": "", "definicao": ""}


def default_campo() -> CampoProcedimento:
    return {"campo": "", "descricao": ""}


def default_item_matriz() -> ItemMatriz:
    return {"tela": "", "nome_tela": "", "etapa": "", "responsavel": ""}


def default_secao() -> Secao:
    return {"titulo": "", "responsavel": "", "passos": [""], "campos": []}


def default_revisao() -> Revisao:
    return {
        "revisao": DEFAULT_VERSAO,
        "data": date.today().strftime(DATE_FORMAT),
        "descricao": "Emissão inicial",
        "responsavel": "",
    }


def empty_revisao() -> Revisao:
    return {"revisao": "", "data": "", "descricao": "", "responsavel": ""}


@dataclass(slots=True)
class PopData:
    nome_pop: str
    codigo: str
    versao: str
    data: str
    area: str
    aviso: str
    objetivo: str
    escopo: str = ""
    campo_aplicacao: str = ""
    pre_condicoes: str = ""
    elaborado_por: str = ""
    elaborado_cargo: str = ""
    aprovado_por: str = ""
    aprovado_cargo: str = ""
    definicoes: list[Definicao] = field(default_factory=list)
    matriz_responsabilidades: list[ItemMatriz] = field(default_factory=list)
    secoes: list[Secao] = field(default_factory=list)
    regras: list[str] = field(default_factory=list)
    consulta: str = ""
    revisoes: list[Revisao] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Fallback de compatibilidade entre escopo e campo_aplicacao
        if not self.campo_aplicacao and self.escopo:
            self.campo_aplicacao = self.escopo
        elif not self.escopo and self.campo_aplicacao:
            self.escopo = self.campo_aplicacao

    @classmethod
    def from_form(
        cls,
        *,
        nome_pop: str,
        codigo: str,
        versao: str,
        data: str,
        area: str,
        aviso: str,
        objetivo: str,
        escopo: str = "",
        campo_aplicacao: str = "",
        pre_condicoes: str = "",
        elaborado_por: str = "",
        elaborado_cargo: str = "",
        aprovado_por: str = "",
        aprovado_cargo: str = "",
        definicoes: list[Definicao] | None = None,
        matriz_responsabilidades: list[ItemMatriz] | None = None,
        secoes: list[Secao] | None = None,
        regras: list[str] | None = None,
        consulta: str = "",
        revisoes: list[Revisao] | None = None,
    ) -> PopData:
        return cls(
            nome_pop=nome_pop.strip(),
            codigo=codigo.strip(),
            versao=versao.strip(),
            data=data.strip(),
            area=area.strip(),
            aviso=aviso.strip(),
            objetivo=objetivo.strip(),
            escopo=escopo.strip(),
            campo_aplicacao=campo_aplicacao.strip() or escopo.strip(),
            pre_condicoes=pre_condicoes.strip(),
            elaborado_por=elaborado_por.strip(),
            elaborado_cargo=elaborado_cargo.strip(),
            aprovado_por=aprovado_por.strip(),
            aprovado_cargo=aprovado_cargo.strip(),
            definicoes=definicoes or [],
            matriz_responsabilidades=matriz_responsabilidades or [],
            secoes=secoes or [],
            regras=regras or [],
            consulta=consulta.strip(),
            revisoes=revisoes or [],
        )

    def validate(self) -> list[str]:
        checks = (
            (self.nome_pop, ValidationMessage.NOME_OBRIGATORIO),
            (self.objetivo, ValidationMessage.OBJETIVO_OBRIGATORIO),
            (self.codigo, ValidationMessage.CODIGO_OBRIGATORIO),
            (self.area, ValidationMessage.AREA_OBRIGATORIA),
        )
        return [message for value, message in checks if not value]

    def output_filename(self) -> str:
        prefix = self.codigo or "POP"
        return f"{prefix}_{_slugify(self.nome_pop)}.docx"


def _slugify(nome: str) -> str:
    """Converte um nome em slug seguro para filename (Windows/macOS/Linux)."""
    slug = re.sub(r"[^\w.-]+", "_", nome.strip()).strip("_")
    return slug[:FILENAME_SLUG_MAX_LEN]
