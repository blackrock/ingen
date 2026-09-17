#  InGen FastAPI wrapper — run history store (pure logic)
#
#  Persists RunRecords as JSON files on disk so GET /api/runs/{id} and /api/runs/history survive
#  restarts. A future swap to a real database keeps the same tiny interface.

import json
import os
from pathlib import Path


class RunStore:
    def __init__(self, base_dir: str):
        self.dir = Path(base_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, run_id: str) -> Path:
        return self.dir / f"{run_id}.json"

    def save(self, record: dict) -> None:
        self._path(record["runId"]).write_text(json.dumps(record), encoding="utf-8")

    def get(self, run_id: str):
        path = self._path(run_id)
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self, config_id: str | None = None):
        records = []
        for f in self.dir.glob("run_*.json"):
            try:
                records.append(json.loads(f.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        if config_id:
            records = [r for r in records if r.get("configId") == config_id]
        records.sort(key=lambda r: r.get("startedAt", ""), reverse=True)
        return records


def default_store() -> RunStore:
    return RunStore(os.environ.get("INGEN_RUNS_DIR", str(Path(__file__).resolve().parent.parent / ".runs")))
