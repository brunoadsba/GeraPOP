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


class Secao(TypedDict):
    titulo: str
    passos: list[str]


class Revisao(TypedDict):
    revisao: str
    data: str
    descricao: str
    responsavel: str


def default_definicao() -> Definicao:
    return {"termo": "", "definicao": ""}


def default_secao() -> Secao:
    return {"titulo": "", "passos": [""]}


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
    escopo: str
    definicoes: list[Definicao] = field(default_factory=list)
    secoes: list[Secao] = field(default_factory=list)
    regras: list[str] = field(default_factory=list)
    consulta: str = ""
    revisoes: list[Revisao] = field(default_factory=list)

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
        escopo: str,
        definicoes: list[Definicao],
        secoes: list[Secao],
        regras: list[str],
        consulta: str,
        revisoes: list[Revisao],
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
            definicoes=definicoes,
            secoes=secoes,
            regras=regras,
            consulta=consulta.strip(),
            revisoes=revisoes,
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
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", nome.strip()).strip("_")
    return slug[:FILENAME_SLUG_MAX_LEN]
