"""Validação dos dados estáticos do fluxo-sev contra os formatos do GeraPOP."""

import json
from pathlib import Path

from gerapop.models import PopData

FLUXO_SEV_DIR = Path(__file__).resolve().parent.parent / "fluxo-sev"


def _ler(relativo: str) -> dict:
    return json.loads((FLUXO_SEV_DIR / relativo).read_text(encoding="utf-8"))


def test_pop_json_e_compativel_com_o_gerapop() -> None:
    payload = _ler("data/pops/pop-desembarque.json")

    assert payload["metadata"]["status"] == "generated"
    pop = PopData(**payload["pop"])
    assert pop.codigo == "POP-MAN-001"
    assert pop.validate() == []
    assert payload["metadata"]["filename"] == pop.output_filename()


def test_fluxo_desembarque_estrutura_valida() -> None:
    fluxo = _ler("data/fluxo-desembarque.json")

    assert fluxo["fluxo_id"] == "desembarque"
    assert len(fluxo["nos"]) >= 6
    ids = [no["id"] for no in fluxo["nos"]]
    assert len(ids) == len(set(ids)), "ids de nós duplicados"

    pops_dir = FLUXO_SEV_DIR / "data/pops"
    for no in fluxo["nos"]:
        assert no["etapa"] >= 1
        if no["pop_ref"] is not None:
            assert (
                pops_dir / f"{no['pop_ref']}.json"
            ).exists(), f"pop_ref {no['pop_ref']} sem arquivo correspondente"

    pop_ids = {no["id"] for no in fluxo["nos"]}
    for link in fluxo.get("links", []):
        assert link["from"] in pop_ids and link["to"] in pop_ids


def test_todos_os_nos_tem_pop_ou_marcados_sem_pop() -> None:
    fluxo = _ler("data/fluxo-desembarque.json")

    assert any(no["pop_ref"] for no in fluxo["nos"]), "pelo menos um nó deve ter POP"
    assert any(no["pop_ref"] is None for no in fluxo["nos"]), "deve haver nó sem POP"
