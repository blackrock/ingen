#  InGen FastAPI wrapper — execution runner (pure logic, no FastAPI import)
#
#  Runs `python -m ingen <config>` as a subprocess and parses its log output into the SAME
#  structured RunRecord shape the frontend already consumes (runId/stages/logs/validation/timings).
#  Keeping this free of FastAPI/pydantic means it is unit-testable with plain Python.
#
#  Structured-result note: InGen logs to a Python logger and writes files; it does not emit machine
#  structured results. So stage status is derived best-effort from its log markers ("Generating
#  interface 'X'", "Successfully generated interface 'X'", "Failed to generate ..."). This is the
#  documented seam where deeper instrumentation could replace heuristics later.

import re
import sys
import tempfile
import time
import uuid
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .validation import derive_validation

STAGE_ORDER_BASE = ["read", "pre_process", "format", "validate", "write"]

# Log markers used to infer how far an interface got before failing.
_STAGE_MARKERS = [
    ("pre_process", re.compile(r"pre-processing", re.I)),
    ("format", re.compile(r"Formatting column", re.I)),
    ("validate", re.compile(r"Validat", re.I)),
    ("write", re.compile(r"writing file|Successfully generated", re.I)),
]
_GEN_RE = re.compile(r"Generating interface '([^']+)'")
_OK_RE = re.compile(r"Successfully generated interface '([^']+)'")
_FAIL_RE = re.compile(r"Failed to generate interface file for (\S+)")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


_LEVEL_RE = re.compile(r"\s-\s(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s-\s")
_LEVEL_MAP = {"CRITICAL": "error", "ERROR": "error", "WARNING": "warn", "DEBUG": "info", "INFO": "info"}


def _level_of(line: str) -> str:
    """Use ingen's ' - LEVEL - ' log prefix; fall back to a narrow heuristic for prefix-less lines
    (e.g. raw traceback lines). Avoids flagging data/columns named 'error' as errors."""
    m = _LEVEL_RE.search(line)
    if m:
        return _LEVEL_MAP[m.group(1)]
    low = line.lower()
    if "traceback" in low or low.startswith("error"):
        return "error"
    return "info"


def _stages_for_interface(iface_cfg: dict):
    stages = ["read", "pre_process"]
    if iface_cfg.get("post_processing"):
        stages.append("post_process")
    stages += ["format", "validate", "write"]
    return stages


def build_run_record(*, config_id, config_name, overrides, started_at, finished_at,
                     duration_ms, exit_code, output, config: dict):
    """Turn captured subprocess output into a RunRecord dict (frontend-compatible)."""
    lines = [ln for ln in output.splitlines() if ln.strip()]
    interfaces_cfg = config.get("interfaces", {}) or {}
    requested = overrides.get("interfaces") or list(interfaces_cfg.keys())

    succeeded = set(_OK_RE.findall(output))
    failed = set(_FAIL_RE.findall(output))
    # If the process crashed before any per-interface marker, treat all requested as failed.
    if exit_code != 0 and not succeeded and not failed:
        failed = set(requested)

    logs = []
    base_ts = started_at
    for ln in lines:
        logs.append({"type": "log", "ts": base_ts, "level": _level_of(ln), "message": ln.strip()})

    stages = []
    for name in requested:
        iface_cfg = interfaces_cfg.get(name, {})
        order = _stages_for_interface(iface_cfg)
        ok = name in succeeded or (name not in failed and exit_code == 0)
        if ok:
            for st in order:
                stages.append({"interface": name, "stage": st, "status": "ok"})
            continue
        # Failed: infer the furthest stage reached from this interface's log slice.
        reached = _furthest_stage(output, name)
        reached_idx = order.index(reached) if reached in order else 0
        for i, st in enumerate(order):
            if i < reached_idx:
                status = "ok"
            elif i == reached_idx:
                status = "failed"
            else:
                status = "skipped"
            stages.append({"interface": name, "stage": st, "status": status})

    validation = derive_validation(config, requested, failed)

    if not failed:
        status = "success"
    elif len(failed) >= len(requested):
        status = "failed"
    else:
        status = "partial"

    return {
        "runId": f"run_{uuid.uuid4().hex[:10]}",
        "configId": config_id,
        "configName": config_name,
        "status": status,
        "startedAt": started_at,
        "finishedAt": finished_at,
        "durationMs": duration_ms,
        "stages": stages,
        "logs": logs,
        "validation": validation,
        "overrides": overrides,
    }


def _furthest_stage(output: str, interface: str) -> str:
    """Best-effort: which stage did `interface` reach before failing? Scans its log slice."""
    gen = re.search(rf"Generating interface '{re.escape(interface)}'", output)
    if not gen:
        return "read"
    rest = output[gen.end():]
    nxt = _GEN_RE.search(rest)
    slice_ = rest[: nxt.start()] if nxt else rest
    reached = "read"
    for stage, rx in _STAGE_MARKERS:
        if rx.search(slice_):
            reached = stage
    return reached


def _as_param_pairs(params) -> list:
    """Render a {key: value} override map as a list of `key=value` argv tokens for InGen.

    Returns [] for empty/None so callers can omit the flag entirely. Values are stringified; keys
    and values are passed through verbatim (InGen splits on the first '=').
    """
    if not params:
        return []
    return [f"{k}={v}" for k, v in params.items()]


def _default_executor(cmd, cwd):
    """Run the real subprocess. Returns (exit_code, combined_output)."""
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=600,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def execute_run(yaml_text: str, overrides: dict, config: dict, *,
                workdir: str = ".", executor=_default_executor) -> dict:
    """Write YAML to a temp file, run `python -m ingen`, return a RunRecord dict.

    `executor` is injectable so the parsing/record-building can be unit-tested without InGen/GE.
    """
    overrides = overrides or {}
    config_id = overrides.get("configId") or config.get("_configId") or "config"
    config_name = overrides.get("configName") or config.get("_configName") or config_id

    started_at = _now_iso()
    t0 = time.time()

    with tempfile.TemporaryDirectory() as tmp:
        cfg_path = Path(tmp) / "interface.yml"
        cfg_path.write_text(yaml_text, encoding="utf-8")

        cmd = [sys.executable, "-m", "ingen", str(cfg_path)]
        if overrides.get("run_date"):
            cmd.append(str(overrides["run_date"]))
        if overrides.get("interfaces"):
            cmd += ["--interfaces", ",".join(overrides["interfaces"])]
        # InGen's KeyValue argparse action RESETS its dict on every occurrence of the flag, so each
        # pair must be passed as additional values of ONE flag (`--query_params a=1 b=2`), not as a
        # repeated flag (`--query_params a=1 --query_params b=2`) which would keep only the last pair.
        query_pairs = _as_param_pairs(overrides.get("query_params"))
        if query_pairs:
            cmd += ["--query_params", *query_pairs]
        override_pairs = _as_param_pairs(overrides.get("override_params"))
        if override_pairs:
            cmd += ["--override_params", *override_pairs]

        try:
            exit_code, output = executor(cmd, workdir)
        except Exception as exc:  # subprocess failure, timeout, etc.
            exit_code, output = 1, f"Wrapper failed to execute InGen: {exc}"

    finished_at = _now_iso()
    duration_ms = int((time.time() - t0) * 1000)

    return build_run_record(
        config_id=config_id, config_name=config_name, overrides=overrides,
        started_at=started_at, finished_at=finished_at, duration_ms=duration_ms,
        exit_code=exit_code, output=output, config=config,
    )
