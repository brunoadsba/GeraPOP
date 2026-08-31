from fastapi import FastAPI, Request
from mangum import Mangum

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok", "from": "vercel"}

@app.get("/api/debug")
def debug(request: Request):
    return {"path": str(request.url.path), "routes": [getattr(r, "path", str(r)) for r in app.routes]}

# importa o app real e mescla rotas
try:
    from backend.main import app as real_app
    for route in real_app.routes:
        path = getattr(route, "path", None)
        if path and path not in [getattr(r, "path", None) for r in app.routes]:
            app.routes.append(route)
except Exception as e:
    @app.get("/api/import-error")
    def import_error():
        return {"error": str(e)}

handler = Mangum(app, lifespan="off")
