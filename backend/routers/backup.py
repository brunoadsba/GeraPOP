"""Download do backup zip."""

from __future__ import annotations

import io
from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from gerapop.storage import gerar_backup_zip

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.get("", response_class=StreamingResponse)
def baixar_backup() -> StreamingResponse:
    """Retorna o zip com todos os POPs salvos e o rascunho."""
    filename = f"gerapop_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return StreamingResponse(
        io.BytesIO(gerar_backup_zip()),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
