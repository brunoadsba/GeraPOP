"""Modelos Pydantic — contrato de request/response da API."""

from pydantic import BaseModel, ConfigDict, Field


class DefinicaoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    termo: str = ""
    definicao: str = ""


class CampoProcedimentoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    campo: str = ""
    descricao: str = ""


class SecaoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    titulo: str = ""
    passos: list[str] = []
    campos: list[CampoProcedimentoSchema] = []


class RevisaoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    revisao: str = ""
    data: str = ""
    descricao: str = ""
    responsavel: str = ""


class PopCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nome_pop: str = Field(default="", description="Nome completo do procedimento")
    codigo: str = Field(default="", description="Código único do POP")
    versao: str = Field(default="01", description="Versão do documento")
    data: str = Field(default="", description="Data de emissão (dd/mm/aaaa)")
    area: str = Field(default="", description="Setor responsável")
    aviso: str = Field(default="", description="Alerta opcional")
    objetivo: str = Field(default="", description="Objetivo do procedimento")
    escopo: str = Field(default="", description="Escopo e pré-condições")
    definicoes: list[DefinicaoSchema] = []
    secoes: list[SecaoSchema] = []
    regras: list[str] = []
    consulta: str = Field(default="", description="Consulta e relatórios")
    revisoes: list[RevisaoSchema] = []


class PopListItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    created_at: str
    status: str
    codigo: str
    nome_pop: str
    filename: str


class ValidationErrorResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    errors: list[str]


class GenerateResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    pop_id: str
    filename: str


class CheckCodeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    codigo: str = ""
    allowed_ids: list[str] = []


class DraftPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    form: dict
    loaded_from_id: str | None = None
