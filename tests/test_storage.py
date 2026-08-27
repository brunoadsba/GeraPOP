import io
import json
import zipfile

import pytest

from gerapop.models import PopData
from gerapop.storage import (
    clear_draft,
    delete_pop,
    gerar_backup_zip,
    get_docx_bytes,
    get_draft,
    get_library_dir,
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


def test_delete_pop_remove_arquivos_e_da_listagem(pop_minimo: PopData) -> None:
    pop_id = save_pop(pop_minimo, b"PK fake docx")

    assert delete_pop(pop_id) is True

    assert get_pop(pop_id) is None
    assert get_docx_bytes(pop_id) is None
    assert get_pop_json_bytes(pop_id) is None
    assert list_pops() == []


def test_delete_pop_inexistente_retorna_false() -> None:
    assert delete_pop("nao_existe") is False


def test_delete_pop_rejeita_id_fora_do_diretorio(tmp_path) -> None:
    # Path traversal: o id resolve para fora de data/pops/ — deve falhar feio.
    with pytest.raises(ValueError):
        delete_pop("../draft.json")


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


def test_gerar_backup_zip_contem_arquivos(pop_minimo: PopData) -> None:
    save_pop(pop_minimo, b"PK fake docx")
    save_draft({"form": {"nome_pop": "Rascunho"}})

    names = zipfile.ZipFile(io.BytesIO(gerar_backup_zip())).namelist()

    assert any(name.endswith("pop.json") for name in names)
    assert any(name.endswith("pop.docx") for name in names)
    assert any(name.endswith("draft.json") for name in names)


def test_gerar_backup_zip_vazio() -> None:
    names = zipfile.ZipFile(io.BytesIO(gerar_backup_zip())).namelist()

    assert names == []


def test_save_pop_organiza_biblioteca_oficial(pop_minimo: PopData) -> None:
    save_pop(pop_minimo, b"PK fake docx", pdf=b"%PDF-fake")

    pasta = get_library_dir() / "POP-OPE-001_REGISTRO DE MANOBRAS"
    assert (pasta / "POP-OPE-001_REGISTRO DE MANOBRAS.docx").read_bytes() == b"PK fake docx"
    assert (pasta / "POP-OPE-001_REGISTRO DE MANOBRAS.pdf").read_bytes() == b"%PDF-fake"


def test_save_pop_mesmo_codigo_renomeia_pasta_da_biblioteca(pop_minimo: PopData) -> None:
    save_pop(pop_minimo, b"docx-v1", pdf=b"pdf-v1")
    pop_minimo.nome_pop = "Programação de Saída"
    save_pop(pop_minimo, b"docx-v2", pdf=b"pdf-v2", pop_id="mesmo")

    lib = get_library_dir()
    nova = lib / "POP-OPE-001_PROGRAMAÇÃO DE SAÍDA"
    assert not (lib / "POP-OPE-001_REGISTRO DE MANOBRAS").exists()
    assert (nova / "POP-OPE-001_PROGRAMAÇÃO DE SAÍDA.docx").read_bytes() == b"docx-v2"
    assert (nova / "POP-OPE-001_PROGRAMAÇÃO DE SAÍDA.pdf").read_bytes() == b"pdf-v2"


def test_delete_pop_remove_pasta_da_biblioteca(pop_minimo: PopData) -> None:
    pop_id = save_pop(pop_minimo, b"PK fake docx", pdf=b"%PDF-fake")
    pasta = get_library_dir() / "POP-OPE-001_REGISTRO DE MANOBRAS"
    assert pasta.is_dir()

    assert delete_pop(pop_id) is True
    assert not pasta.exists()
