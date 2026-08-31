"""Aplicação FastAPI do GeraPOP."""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.routers import attach, backup, drafts, generate, pops

app = FastAPI(title="GeraPOP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(attach.router)
app.include_router(pops.router)
app.include_router(generate.router)
app.include_router(drafts.router)
app.include_router(backup.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    from fastapi import Request

    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
    async def serve_frontend(request: Request, full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        if request.method != "GET":
            raise HTTPException(status_code=404, detail="Not found")
        file_path = frontend_dist / full_path
        if full_path and file_path.is_file():
            return FileResponse(str(file_path))
        index = frontend_dist / "index.html"
        if index.is_file():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Not found")
