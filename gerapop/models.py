from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TypedDict


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
        errors: list[str] = []
        if not self.nome_pop:
            errors.append("Nome do POP é obrigatório.")
        if not self.objetivo:
            errors.append("Objetivo é obrigatório.")
        if not self.codigo:
            errors.append("Código é obrigatório.")
        if not self.area:
            errors.append("Área é obrigatória.")
        return errors

    def output_filename(self) -> str:
        slug = self.nome_pop[:30].replace(" ", "_").replace("/", "-")
        prefix = self.codigo or "POP"
        return f"{prefix}_{slug}.docx"


def default_revisao() -> Revisao:
    return {
        "revisao": "01",
        "data": date.today().strftime("%d/%m/%Y"),
        "descricao": "Emissão inicial",
        "responsavel": "",
    }
