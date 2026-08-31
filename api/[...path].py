from fastapi import FastAPI, Request
from mangum import Mangum

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "from": "mangum"}

@app.get("/api/debug")
def debug(request: Request):
    return {"path": str(request.url.path), "routes": [getattr(r, "path", str(r)) for r in app.routes]}

@app.get("/{full_path:path}")
def catch_all(full_path: str, request: Request):
    return {"catch_all_path": full_path, "url_path": str(request.url.path), "routes": [getattr(r, "path", str(r)) for r in app.routes]}

# tenta importar o app real e mesclar
try:
    from backend.main import app as real_app
    for route in real_app.routes:
        if getattr(route, "path", None) not in [getattr(r, "path", None) for r in app.routes]:
            app.routes.append(route)
except Exception as e:
    @app.get("/api/import-error")
    def import_error():
        return {"error": str(e)}

handler = Mangum(app, lifespan="off")
