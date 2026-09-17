# InGen FastAPI Wrapper

A thin HTTP service that runs `python -m ingen` and returns structured execution results to the
InGen Studio frontend. It adds no logic to InGen — it shells out to the CLI and parses the output.

## Run

From the **repository root** (so the sample configs' relative paths resolve):

```bash
pip install -r backend/requirements.txt   # fastapi, uvicorn, pyyaml
pip install -e .                           # InGen itself (pandas, great_expectations, ...)

uvicorn backend.app.main:app --reload --port 8000
```

The Next.js dev server (port 3000, legacy Vite port 5173) is allowed via CORS by default.

## Environment

| Var | Default | Purpose |
|-----|---------|---------|
| `INGEN_WORKDIR` | process cwd | Working directory for the `python -m ingen` subprocess (where data/output paths resolve). |
| `INGEN_RUNS_DIR` | `backend/.runs` | Where RunRecords are persisted (history). |
| `INGEN_CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:5173,http://127.0.0.1:5173` | Comma-separated allowed origins. |

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET`  | `/api/health` | Liveness check. |
| `POST` | `/api/files/upload` | Upload a sample data file; returns a parsed preview (size/type capped). |
| `POST` | `/api/sources/columns` | Fetch the column names a configured source would produce. |
| `POST` | `/api/configs/validate` | Schema/cross-reference validation of a YAML config (no run). |
| `POST` | `/api/runs` | Write YAML to temp, run InGen, return a structured RunRecord. |
| `GET`  | `/api/runs/history?config_id=` | List past RunRecords. |
| `GET`  | `/api/runs/{run_id}` | One RunRecord. |
| `GET`  | `/api/runs/{run_id}/logs` | The run's log lines. |
| `GET`  | `/api/runs/{run_id}/validation` | The run's validation report. |

## Trust boundary

This wrapper executes whatever the posted config says (file reads, SQL, API calls — InGen's
nature). It is intended for **local/trusted development**. Authentication, sandboxing, and network
egress controls are intentionally out of scope here.
