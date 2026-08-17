"""Aplicação FastAPI do GeraPOP."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers import backup, drafts, generate, pops

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

app.include_router(pops.router)
app.include_router(generate.router)
app.include_router(drafts.router)
app.include_router(backup.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
