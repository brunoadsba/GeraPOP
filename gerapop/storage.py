"""Persistência dos POPs gerados em disco (JSON + .docx por registro)."""

from __future__ import annotations

import io
import json
import os
import shutil
import uuid
import zipfile
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from gerapop.models import PopData

STORAGE_DIR_ENV = "GERAPOP_DATA_DIR"
DEFAULT_STORAGE_DIR = "data"
DRAFT_FILENAME = "draft.json"


def get_storage_dir() -> Path:
    return Path(os.environ.get(STORAGE_DIR_ENV, DEFAULT_STORAGE_DIR)).resolve()


def _pops_dir() -> Path:
    return get_storage_dir() / "pops"


def _pop_dir(pop_id: str) -> Path:
    return _pops_dir() / pop_id


def serialize_pop(pop: PopData, created_at: datetime | None = None) -> dict[str, Any]:
    """Serializa um PopData no formato reutilizável (metadata + pop)."""
    metadata = {
        "created_at": (created_at or datetime.now()).isoformat(),
        "status": "generated",
        "codigo": pop.codigo,
        "nome_pop": pop.nome_pop,
        "filename": pop.output_filename(),
    }
    return {"metadata": metadata, "pop": asdict(pop)}


_ULTIMO_TIMESTAMP: datetime | None = None


def _proximo_timestamp() -> datetime:
    """Garante timestamps estritamente crescentes entre chamadas no mesmo processo."""
    global _ULTIMO_TIMESTAMP
    agora = datetime.now()
    if _ULTIMO_TIMESTAMP is not None and agora <= _ULTIMO_TIMESTAMP:
        agora = _ULTIMO_TIMESTAMP + timedelta(microseconds=1)
    _ULTIMO_TIMESTAMP = agora
    return agora


def save_pop(pop: PopData, docx: bytes | None = None, pop_id: str | None = None) -> str:
    if not pop_id:
        timestamp = _proximo_timestamp()
        pop_id = timestamp.strftime("%Y%m%d_%H%M%S_%f") + "_" + uuid.uuid4().hex[:6]
    else:
        timestamp = datetime.now()
    target = _pop_dir(pop_id)
    target.mkdir(parents=True, exist_ok=True)
    payload = serialize_pop(pop, created_at=timestamp)
    _atomic_write(target / "pop.json", json.dumps(payload, ensure_ascii=False, indent=2))
    if docx is not None:
        _atomic_write(target / "pop.docx", docx)
    return pop_id


def list_pops() -> list[dict[str, Any]]:
    pops_dir = _pops_dir()
    if not pops_dir.exists():
        return []
    records: list[dict[str, Any]] = []
    for entry in pops_dir.iterdir():
        json_path = entry / "pop.json"
        if not entry.is_dir() or not json_path.exists():
            continue
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        records.append({"id": entry.name, **payload["metadata"]})
    return sorted(records, key=lambda record: record["created_at"], reverse=True)


def get_pop(pop_id: str) -> PopData | None:
    path = _pop_dir(pop_id) / "pop.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return PopData(**payload["pop"])


def get_docx_bytes(pop_id: str) -> bytes | None:
    path = _pop_dir(pop_id) / "pop.docx"
    try:
        return path.read_bytes()
    except OSError:
        return None


def get_pop_json_bytes(pop_id: str) -> bytes | None:
    """Bytes do pop.json salvo (mesmo conteúdo exportado para download)."""
    path = _pop_dir(pop_id) / "pop.json"
    try:
        return path.read_bytes()
    except OSError:
        return None


def delete_pop(pop_id: str) -> bool:
    """Exclui um POP salvo (pasta `data/pops/<pop_id>` com pop.json + pop.docx).

    Retorna ``True`` quando a pasta existia e foi removida; ``False`` quando o
    POP não existe. Levanta ``ValueError`` se o id escapar de ``data/pops/``
    (defesa contra path traversal — ids vêm do selectbox do histórico).
    """
    target = _pop_dir(pop_id)
    pops_dir = _pops_dir()
    target_resolved = target.resolve()
    if pops_dir.resolve() not in target_resolved.parents:
        raise ValueError(f"pop_id inválido: {pop_id!r}")
    if not target_resolved.exists():
        return False
    shutil.rmtree(target_resolved)
    return True


def _draft_path() -> Path:
    return get_storage_dir() / DRAFT_FILENAME


def save_draft(payload: dict[str, Any]) -> None:
    """Persiste o rascunho do formulário (substitui o anterior)."""
    _atomic_write(_draft_path(), json.dumps(payload, ensure_ascii=False, indent=2))


def get_draft() -> dict[str, Any] | None:
    """Lê o rascunho salvo; None quando não existe ou está corrompido."""
    path = _draft_path()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def clear_draft() -> None:
    try:
        _draft_path().unlink()
    except FileNotFoundError:
        pass


def gerar_backup_zip() -> bytes:
    """Zip em memória com todos os POPs salvos e o rascunho."""
    buffer = io.BytesIO()
    storage_dir = get_storage_dir()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(storage_dir.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(storage_dir))
    return buffer.getvalue()


def _atomic_write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8") if isinstance(content, str) else content
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)
