from fastapi import FastAPI
from pydantic import BaseModel
from .scanner import scan_diff

app = FastAPI(title="CI/CD AI Guardrails", version="0.1.0")

class ScanRequest(BaseModel):
    repo: str
    diff: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/scan")
def scan(req: ScanRequest):
    result = scan_diff(req.repo, req.diff)
    return {"tool": "guardrails", **result}
