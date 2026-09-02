"""Geração e download de documentos (.docx / .pdf)."""

from __future__ import annotations

import io
import urllib.parse
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.dependencies import pop_from_request
from backend.schemas import GenerateResponse, PopCreateRequest
from gerapop.codigo import encontrar_codigo_duplicado
from gerapop.constants import DOCX_MIME, PDF_MIME
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf
from gerapop.storage import (
    _nome_pasta_biblioteca,
    get_docx_bytes,
    get_library_dir,
    get_pop,
    list_pops,
    save_pop,
)

router = APIRouter(prefix="/api/generate", tags=["generate"])


def _nome_pdf(nome_docx: str) -> str:
    return nome_docx.removesuffix(".docx") + ".pdf"


def _block_if_duplicado(payload: PopCreateRequest, allowed_ids: list[str]) -> None:
    pop = pop_from_request(payload)
    duplicado = encontrar_codigo_duplicado(pop.codigo, list_pops(), set(allowed_ids))
    if duplicado is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"O código {pop.codigo} já é usado pelo POP "
                f"'{duplicado['nome_pop']}' (criado em {duplicado['created_at'][:16]}). "
                "Use um código diferente ou carregue o POP existente para editá-lo."
            ),
        )


@router.post("", response_model=GenerateResponse)
def gerar_pop(
    payload: PopCreateRequest,
    allowed_ids: list[str] | None = Query(default=None),
) -> GenerateResponse:
    """Valida, salva o POP e retorna seu id + nome do arquivo .docx."""
    pop = pop_from_request(payload)
    if pop.validate():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=[str(error) for error in pop.validate()],
        )
    _block_if_duplicado(payload, allowed_ids or [])
    target_id = allowed_ids[0] if (allowed_ids and len(allowed_ids) == 1) else None
    pop_id = save_pop(
        pop,
        gerar_docx(pop).getvalue(),
        pop_id=target_id,
        pdf=gerar_pdf(pop).getvalue(),
    )
    return GenerateResponse(pop_id=pop_id, filename=pop.output_filename())


def _stream(data: bytes | io.BytesIO, media_type: str, filename: str) -> StreamingResponse:
    """Streams bytes ou BytesIO como attachment com o nome informado (RFC 5987 para acentos)."""
    if hasattr(data, "getvalue"):
        body = data
    else:
        body = io.BytesIO(data)
    # Fallback ASCII sem acentos + UTF-8 encoded para suportar "ANÚNCIO", "PROGRAMAÇÃO" no Vercel/Chrome
    fallback = filename.encode("ascii", "ignore").decode() or "arquivo"
    quoted = urllib.parse.quote(filename, safe="")
    disposition = f'attachment; filename="{fallback}"; filename*=UTF-8\'\'{quoted}'
    return StreamingResponse(
        body,
        media_type=media_type,
        headers={"Content-Disposition": disposition},
    )


def _bytes_da_biblioteca(pop, ext: str) -> bytes | None:
    """Retorna bytes do arquivo da biblioteca local se existir (fonte da verdade 607K)."""
    try:
        lib_dir = get_library_dir() / _nome_pasta_biblioteca(pop)
        stem = lib_dir.name
        candidate = lib_dir / f"{stem}{ext}"
        if candidate.is_file():
            return candidate.read_bytes()
        # fallback: varre pasta do código caso nome tenha mudado
        if lib_dir.parent.exists():
            for entry in lib_dir.parent.iterdir():
                if entry.is_dir() and entry.name.startswith(pop.codigo + "_"):
                    alt = entry / f"{entry.name}{ext}"
                    if alt.is_file():
                        return alt.read_bytes()
    except Exception:
        return None
    return None


@router.post("/preview/docx", response_class=StreamingResponse)
def preview_docx(payload: PopCreateRequest) -> StreamingResponse:
    """Gera o .docx sem salvar (para preview/download imediato)."""
    pop = pop_from_request(payload)
    return _stream(gerar_docx(pop), DOCX_MIME, pop.output_filename())


@router.post("/preview/pdf", response_class=StreamingResponse)
def preview_pdf(payload: PopCreateRequest) -> StreamingResponse:
    """Gera o .pdf sem salvar."""
    pop = pop_from_request(payload)
    return _stream(gerar_pdf(pop), PDF_MIME, _nome_pdf(pop.output_filename()))


@router.get("/{pop_id}/docx", response_class=StreamingResponse)
def baixar_docx(pop_id: str) -> StreamingResponse:
    """Retorna o .docx do POP salvo (prioriza biblioteca local 56K correta)."""
    pop = get_pop(pop_id)
    if pop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POP não encontrado")
    data = _bytes_da_biblioteca(pop, ".docx") or get_docx_bytes(pop_id) or gerar_docx(pop).getvalue()
    return _stream(data, DOCX_MIME, pop.output_filename())


@router.get("/{pop_id}/pdf", response_class=StreamingResponse)
def baixar_pdf(pop_id: str) -> StreamingResponse:
    """Retorna o .pdf (prioriza biblioteca local 607K 3p correta, evita truncagem 40K 1p)."""
    pop = get_pop(pop_id)
    if pop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POP não encontrado")
    data = _bytes_da_biblioteca(pop, ".pdf")
    if data is None:
        data = gerar_pdf(pop).getvalue()
    return _stream(data, PDF_MIME, _nome_pdf(pop.output_filename()))
