from backend.main import app

@app.get("/api/debug")
def debug():
    return {"routes": [getattr(r, "path", str(r)) for r in app.routes]}
