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
        objetivo=payload.objetivo,
        escopo=payload.escopo,
        definicoes=[d.model_dump() for d in payload.definicoes],
        secoes=[
            {
                "titulo": s.titulo,
                "passos": list(s.passos),
                "campos": [c.model_dump() for c in s.campos],
            }
            for s in payload.secoes
        ],
        regras=list(payload.regras),
        consulta=payload.consulta,
        revisoes=[r.model_dump() for r in payload.revisoes],
    )


def pop_as_dict(pop: PopData) -> dict:
    """Serializa um PopData como dict para a resposta da API."""
    return asdict(pop)
