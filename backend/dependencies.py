"""Helpers compartilhados dos routers (conversões e fluxo)."""

from __future__ import annotations

from dataclasses import asdict

from backend.schemas import PopCreateRequest
from gerapop.models import PopData


def pop_from_request(payload: PopCreateRequest) -> PopData:
    """Converte o schema Pydantic em PopData (normaliza com .strip())."""
    return PopData.from_form(
        nome_pop=payload.nome_pop,
        codigo=payload.codigo,
        versao=payload.versao,
        data=payload.data,
        area=payload.area,
        aviso=payload.aviso,
        elaborado_por=payload.elaborado_por,
        elaborado_cargo=payload.elaborado_cargo,
        aprovado_por=payload.aprovado_por,
        aprovado_cargo=payload.aprovado_cargo,
        objetivo=payload.objetivo,
        campo_aplicacao=payload.campo_aplicacao or payload.escopo,
        pre_condicoes=payload.pre_condicoes,
        escopo=payload.escopo or payload.campo_aplicacao,
        definicoes=[d.model_dump() for d in payload.definicoes],
        matriz_responsabilidades=[m.model_dump() for m in payload.matriz_responsabilidades],
        secoes=[
            {
                "titulo": s.titulo,
                "responsavel": s.responsavel,
                "responsaveis": list(s.responsaveis),
                "passos": list(s.passos),
                "campos": [c.model_dump() for c in s.campos],
            }
            for s in payload.secoes
        ],
        regras=list(payload.regras),
        consulta=payload.consulta,
        registros_obrigatorios=[r.model_dump() for r in payload.registros_obrigatorios],
        criterios_encerramento=payload.criterios_encerramento,
        indicadores=payload.indicadores,
        aviso_final=payload.aviso_final,
        revisoes=[r.model_dump() for r in payload.revisoes],
    )


def pop_as_dict(pop: PopData) -> dict:
    """Serializa um PopData como dict para a resposta da API."""
    return asdict(pop)
