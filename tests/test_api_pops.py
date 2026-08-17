"""Testes de integração da API FastAPI (TestClient)."""

from fastapi.testclient import TestClient

from backend.main import app
from gerapop.models import default_revisao

client = TestClient(app)


def _promo() -> dict:
    return {
        "nome_pop": "Registro de Manobras",
        "codigo": "POP-OPE-001",
        "versao": "01",
        "data": "01/01/2026",
        "area": "Operações Portuárias",
        "aviso": "",
        "objetivo": "Padronizar o registro de manobras.",
        "escopo": "Aplica-se à equipe de operações.",
        "definicoes": [{"termo": "TOS", "definicao": "Terminal Operating System"}],
        "secoes": [
            {
                "titulo": "Atracação",
                "passos": ["Verificar condições.", "Registrar no sistema."],
                "campos": [],
            }
        ],
        "regras": ["Não executar sem autorização."],
        "consulta": "Menu > Operações > Manobras",
        "revisoes": [default_revisao()],
    }


def _invalido() -> dict:
    return {
        "nome_pop": "",
        "codigo": "",
        "versao": "01",
        "data": "01/01/2026",
        "area": "",
        "aviso": "",
        "objetivo": "",
        "escopo": "",
        "definicoes": [],
        "secoes": [],
        "regras": [],
        "consulta": "",
        "revisoes": [],
    }


def test_health_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_crud_completo() -> None:
    created = client.post("/api/generate", json=_promo())
    assert created.status_code == 200, created.text
    result = created.json()
    pop_id = result["pop_id"]
    assert result["filename"].endswith(".docx")

    listing = client.get("/api/pops")
    assert listing.status_code == 200
    assert any(record["id"] == pop_id for record in listing.json())

    detail = client.get(f"/api/pops/{pop_id}")
    assert detail.status_code == 200
    assert detail.json()["codigo"] == "POP-OPE-001"

    deleted = client.delete(f"/api/pops/{pop_id}")
    assert deleted.status_code == 204

    assert client.get(f"/api/pops/{pop_id}").status_code == 404


def test_validacao_campos_obrigatorios() -> None:
    response = client.post("/api/pops/validate", json=_invalido())
    assert response.status_code == 200
    assert len(response.json()["errors"]) == 4


def test_generate_invalido_retorna_422() -> None:
    response = client.post("/api/generate", json=_invalido())
    assert response.status_code == 422
    assert len(response.json()["detail"]) == 4


def test_unicidade_de_codigo() -> None:
    client.post("/api/generate", json=_promo())

    duplicado = client.post(
        "/api/pops/check-code", json={"codigo": "POP-OPE-001", "allowed_ids": []}
    )
    assert duplicado.status_code == 200
    assert duplicado.json()["codigo"] == "POP-OPE-001"

    sem_conflito = client.post(
        "/api/pops/check-code",
        json={"codigo": "POP-OPE-001", "allowed_ids": [duplicado.json()["id"]]},
    )
    assert sem_conflito.json() is None


def test_generate_duplicado_retorna_409() -> None:
    client.post("/api/generate", json=_promo())
    response = client.post("/api/generate", json=_promo())
    assert response.status_code == 409


def test_download_docx_e_pdf() -> None:
    result = client.post("/api/generate", json=_promo()).json()
    pop_id = result["pop_id"]

    docx = client.get(f"/api/generate/{pop_id}/docx")
    assert docx.status_code == 200
    assert docx.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert len(docx.content) > 0

    pdf = client.get(f"/api/generate/{pop_id}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert len(pdf.content) > 0


def test_preview_docx_sem_salvar() -> None:
    response = client.post("/api/generate/preview/docx", json=_promo())
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats")


def test_preview_pdf_sem_salvar() -> None:
    response = client.post("/api/generate/preview/pdf", json=_promo())
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_draft_save_load_clear() -> None:
    payload = {"form": {"nome_pop": "rascunho"}, "loaded_from_id": None}
    assert client.put("/api/draft", json=payload).status_code == 200

    loaded = client.get("/api/draft")
    assert loaded.status_code == 200
    assert loaded.json()["form"]["nome_pop"] == "rascunho"

    assert client.delete("/api/draft").status_code == 200
    assert client.get("/api/draft").json() is None


def test_backup_zip() -> None:
    response = client.get("/api/backup")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert len(response.content) > 0


def test_exclusao_anti_traversal() -> None:
    response = client.delete("/api/pops/../../fora")
    assert response.status_code in (400, 404)


def test_fluxo_endpoints() -> None:
    fluxo = client.get("/api/pops/fluxo")
    assert fluxo.status_code == 200
    assert fluxo.json() is not None
    assert len(fluxo.json()["nos"]) >= 6

    pop = client.get("/api/pops/fluxo/pop-desembarque")
    assert pop.status_code == 200
    assert pop.json()["codigo"] == "POP-MAN-001"

    missing = client.get("/api/pops/fluxo/nao-existe")
    assert missing.status_code == 404


def test_pop_sem_nome_usa_codigo_no_filename() -> None:
    payload = _promo()
    payload["nome_pop"] = "Manobras / Desembarque (tarde)"
    result = client.post("/api/generate", json=payload).json()
    assert "Manobras" in result["filename"]
    assert "/" not in result["filename"]
