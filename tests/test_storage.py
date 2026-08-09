import json

from gerapop.models import PopData
from gerapop.storage import (
    clear_draft,
    get_docx_bytes,
    get_draft,
    get_pop,
    get_pop_json_bytes,
    get_storage_dir,
    list_pops,
    save_draft,
    save_pop,
    serialize_pop,
)


def test_serialize_pop_round_trip(pop_minimo: PopData) -> None:
    payload = serialize_pop(pop_minimo)

    assert payload["metadata"]["codigo"] == "POP-OPE-001"
    assert payload["metadata"]["filename"].endswith(".docx")
    assert PopData(**payload["pop"]) == pop_minimo


def test_save_e_load_round_trip(pop_minimo: PopData) -> None:
    pop_id = save_pop(pop_minimo, b"PK fake docx")

    assert get_pop(pop_id) == pop_minimo
    assert get_docx_bytes(pop_id) == b"PK fake docx"


def test_get_pop_json_bytes_valido(pop_minimo: PopData) -> None:
    pop_id = save_pop(pop_minimo, b"PK fake docx")

    raw = get_pop_json_bytes(pop_id)
    assert raw is not None
    payload = json.loads(raw.decode("utf-8"))
    assert payload["metadata"]["codigo"] == "POP-OPE-001"
    assert PopData(**payload["pop"]) == pop_minimo


def test_save_sem_docx_retorna_none_no_docx(pop_minimo: PopData) -> None:
    pop_id = save_pop(pop_minimo)

    assert get_docx_bytes(pop_id) is None


def test_list_pops_ordena_mais_recente_primeiro(pop_minimo: PopData) -> None:
    older_id = save_pop(pop_minimo)
    pop_minimo.codigo = "POP-OPE-002"
    newer_id = save_pop(pop_minimo)

    records = list_pops()

    assert [record["id"] for record in records] == [newer_id, older_id]
    assert records[0]["codigo"] == "POP-OPE-002"
    assert records[0]["filename"].endswith(".docx")


def test_list_pops_vazio_sem_diretorio() -> None:
    assert list_pops() == []


def test_get_pop_inexistente_retorna_none() -> None:
    assert get_pop("nao_existe") is None
    assert get_docx_bytes("nao_existe") is None
    assert get_pop_json_bytes("nao_existe") is None


def test_draft_round_trip() -> None:
    assert get_draft() is None

    payload = {"session_id": "abc", "form": {"nome_pop": "Rascunho"}}
    save_draft(payload)

    assert get_draft() == payload

    clear_draft()
    assert get_draft() is None


def test_get_draft_arquivo_corrompido() -> None:
    (get_storage_dir() / "draft.json").write_text("{corrompido", encoding="utf-8")

    assert get_draft() is None
