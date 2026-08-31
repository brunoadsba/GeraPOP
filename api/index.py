from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "from": "standalone"}

@app.get("/api/debug")
def debug():
    return {"routes": [getattr(r, "path", str(r)) for r in app.routes]}

# tenta importar o app real e mesclar rotas se possível
try:
    from backend.main import app as real_app
    # copia rotas do app real para este app
    for route in real_app.routes:
        app.routes.append(route)
except Exception as e:
    @app.get("/api/import-error")
    def import_error():
        return {"error": str(e)}
