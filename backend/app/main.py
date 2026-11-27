#  InGen FastAPI wrapper — HTTP surface (thin)
#
#  Routes only: parse the request, delegate to the pure modules (schema_validate / runner / store),
#  return JSON. No business logic here. Run with:
#     uvicorn backend.app.main:app --reload --port 8000   (from the repo root)

import os

import yaml
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .runner import execute_run
from .schema_validate import validate_yaml
from .store import default_store
from .files import save_and_parse
from .columns import source_columns

app = FastAPI(title="InGen Wrapper", version="1.0.0")

# Allow the Next dev server (3000) — and the legacy Vite port — to call the API in development.
_DEFAULT_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173"
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("INGEN_CORS_ORIGINS", _DEFAULT_ORIGINS).split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE = default_store()
WORKDIR = os.environ.get("INGEN_WORKDIR", os.getcwd())


class ValidateRequest(BaseModel):
    yaml: str


class RunRequest(BaseModel):
    yaml: str
    configId: str | None = None
    configName: str | None = None
    run_date: str | None = None
    interfaces: list[str] | None = None
    query_params: dict | None = None
    override_params: dict | None = None


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    try:
        return save_and_parse(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class ColumnsRequest(BaseModel):
    source: dict
    run_date: str | None = None


@app.post("/api/sources/columns")
def fetch_source_columns(req: ColumnsRequest):
    try:
        return source_columns(req.source, req.run_date)
    except Exception as exc:  # missing file, bad query, auth, unknown type → client shows the message
        raise HTTPException(status_code=400, detail=f"Couldn't read columns: {exc}")


@app.post("/api/configs/validate")
def validate_config(req: ValidateRequest):
    return validate_yaml(req.yaml)


@app.post("/api/runs")
def create_run(req: RunRequest):
    try:
        config = yaml.safe_load(req.yaml) or {}
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}")
    if not isinstance(config, dict):
        raise HTTPException(status_code=400, detail="YAML must be a mapping.")

    overrides = {
        "configId": req.configId,
        "configName": req.configName,
        "run_date": req.run_date,
        "interfaces": req.interfaces,
        "query_params": req.query_params,
        "override_params": req.override_params,
    }
    record = execute_run(req.yaml, overrides, config, workdir=WORKDIR)
    STORE.save(record)
    return record


@app.get("/api/runs/history")
def run_history(config_id: str | None = None):
    return STORE.list(config_id)


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    record = STORE.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    return record


@app.get("/api/runs/{run_id}/logs")
def get_run_logs(run_id: str):
    record = STORE.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    return {"logs": record.get("logs", [])}


@app.get("/api/runs/{run_id}/validation")
def get_run_validation(run_id: str):
    record = STORE.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    return record.get("validation", {"results": [], "summary": {"passed": 0, "failed": 0, "warning": 0, "total": 0}})
