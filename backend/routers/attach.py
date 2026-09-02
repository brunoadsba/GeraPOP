"""Anexar POPs externos — docx/pdf soltos na biblioteca oficial sem passar pelo formulário."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from gerapop.storage import get_library_dir, get_storage_dir

router = APIRouter(prefix="/api/pops", tags=["pops"])

_CHARS_INVALIDOS = re.compile(r'[<>:"/\\|?*]')


def _slug_codigo(codigo: str) -> str:
    return codigo.strip().upper().replace(" ", "_")


def _nome_pasta(codigo: str, nome: str) -> str:
    codigo_norm = codigo.strip()
    nome_limpo = _CHARS_INVALIDOS.sub(" ", nome.strip())
    nome_limpo = re.sub(r"\s+", " ", nome_limpo).strip().upper()
    return f"{codigo_norm}_{nome_limpo}" if nome_limpo else codigo_norm


@router.post("/attach", status_code=status.HTTP_201_CREATED)
async def anexar_pop_externo(
    codigo: str = Form(..., description="Código do POP, ex: POP-OPE-003"),
    nome: str = Form(..., description="Nome do POP"),
    file: UploadFile = File(..., description="Arquivo .docx ou .pdf do POP externo"),
) -> dict:
    if not codigo.strip() or not nome.strip():
        raise HTTPException(status_code=400, detail="codigo e nome são obrigatórios")
    if not file.filename:
        raise HTTPException(status_code=400, detail="arquivo obrigatório")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".docx", ".pdf"):
        raise HTTPException(status_code=400, detail="apenas .docx ou .pdf são aceitos")
    try:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        if size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="arquivo muito grande (máx 10MB)")
    except HTTPException:
        raise
    except Exception:
        try:
            file.file.seek(0)
        except Exception:
            pass

    pasta_nome = _nome_pasta(codigo, nome)
    library_root = get_library_dir()
    try:
        library_root.mkdir(parents=True, exist_ok=True)
        writable = os.access(library_root, os.W_OK)
    except Exception:
        writable = False

    dest_root = library_root if writable else Path(tempfile.gettempdir()) / "gerapop-biblioteca"
    dest_root.mkdir(parents=True, exist_ok=True)
    dest_dir = dest_root / pasta_nome
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / f"{pasta_nome}{ext}"
    try:
        with dest_path.open("wb") as out:
            shutil.copyfileobj(file.file, out)
    finally:
        await file.close()

    pops_root = get_storage_dir() / "pops"
    try:
        pops_root.mkdir(parents=True, exist_ok=True)
        data_writable = os.access(pops_root, os.W_OK)
    except Exception:
        data_writable = False
    if not data_writable:
        pops_root = Path(tempfile.gettempdir()) / "gerapop-data" / "pops"
        pops_root.mkdir(parents=True, exist_ok=True)

    import json
    import time

    pop_id = f"{int(time.time()*1000)}_{os.urandom(4).hex()}"
    pop_dir = pops_root / pop_id
    pop_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "metadata": {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "status": "anexado",
            "codigo": _slug_codigo(codigo),
            "nome_pop": nome.strip(),
            "filename": dest_path.name,
        },
        "pop": {
            "nome_pop": nome.strip(),
            "codigo": _slug_codigo(codigo),
            "versao": "01",
            "data": time.strftime("%d/%m/%Y"),
            "area": "",
            "objetivo": f"POP externo anexado: {dest_path.name}",
        },
    }
    with (pop_dir / "pop.json").open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    # Copia o arquivo também para data/pops/<id>/
    shutil.copy2(dest_path, pop_dir / dest_path.name)

    return {
        "id": pop_id,
        "codigo": _slug_codigo(codigo),
        "nome_pop": nome.strip(),
        "arquivo": str(dest_path),
        "biblioteca": str(dest_dir),
        "aviso": "Em Vercel o arquivo fica em /tmp (efêmero) — baixe o backup zip após anexar. Em Docker/local fica persistido."
        if not writable
        else "Anexado na biblioteca oficial",
    }
