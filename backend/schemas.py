"""Modelos Pydantic — contrato de request/response da API."""

from pydantic import BaseModel, ConfigDict, Field


class DefinicaoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    termo: str = ""
    definicao: str = ""


class ItemMatrizSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    tela: str = ""
    nome_tela: str = ""
    etapa: str = ""
    responsavel: str = ""
    registro: str = ""
    atividade: str = ""


class RegistroObrigatorioSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    registro: str = ""
    conteudo: str = ""
    responsavel: str = ""


class CampoProcedimentoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    campo: str = ""
    descricao: str = ""


class SecaoSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    titulo: str = ""
    responsavel: str = ""
    responsaveis: list[str] = []
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
    elaborado_por: str = Field(default="", description="Nome do elaborador")
    elaborado_cargo: str = Field(default="", description="Cargo do elaborador")
    aprovado_por: str = Field(default="", description="Nome do aprovador")
    aprovado_cargo: str = Field(default="", description="Cargo do aprovador")
    objetivo: str = Field(default="", description="Objetivo do procedimento")
    campo_aplicacao: str = Field(default="", description="Campo de aplicação")
    pre_condicoes: str = Field(default="", description="Pré-condições")
    escopo: str = Field(default="", description="Escopo / Campo de Aplicação (legado)")
    definicoes: list[DefinicaoSchema] = []
    matriz_responsabilidades: list[ItemMatrizSchema] = []
    secoes: list[SecaoSchema] = []
    regras: list[str] = []
    consulta: str = Field(default="", description="Consulta e relatórios")
    registros_obrigatorios: list[RegistroObrigatorioSchema] = []
    criterios_encerramento: str = Field(default="", description="Critérios de encerramento")
    indicadores: str = Field(default="", description="Indicadores de acompanhamento")
    aviso_final: str = Field(default="", description="Aviso/nota final em destaque")
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
