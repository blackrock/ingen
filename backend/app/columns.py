#  InGen wrapper — read a source's column names from its first row (pure logic, no FastAPI import).
#
#  Reuses ingen's own SourceFactory + readers so per-type parsing is never reinvented: build the
#  source, fetch(), hand back df.columns. Works for any configured source — a file path the user
#  typed (not just uploads), a MySQL query, an API endpoint.

from pathlib import Path

from ingen.data_source.source_factory import SourceFactory

PREVIEW_ROWS = 5  # we only need the header; never read the whole source for "show columns"


def source_columns(source: dict, run_date=None) -> dict:
    """Column names for one source dict (same shape the frontend serializes).

    Returns {"columns": [...]}. Raises on read failure (missing file, bad query, auth) — the route
    maps that to a 4xx with the message.
    """
    if not isinstance(source, dict) or not source.get("type"):
        raise ValueError("source must be an object with a 'type'")

    # File sources: read only the first few rows for the header — never the whole file.
    if source.get("type") == "file" and source.get("file_path"):
        try:
            from .files import _parse
        except ImportError:  # run as a script (self-check) — no package context
            from files import _parse
        cols, _preview = _parse(Path(source["file_path"]), n=PREVIEW_ROWS)
        return {"columns": cols}

    # Non-file (mysql/api/json): fall back to ingen's reader.
    # ponytail: we don't rewrite user SQL to inject LIMIT — a row cap belongs in the source config;
    #           tighten here if a live DB/API read ever bites.
    params_map = {"run_date": run_date} if run_date else None
    src = SourceFactory().parse_source(source, params_map)
    df = src.fetch()
    return {"columns": [str(c) for c in df.columns]}


if __name__ == "__main__":
    # Self-check: a CSV file source resolves to its header row.
    import csv
    import tempfile
    from pathlib import Path

    d = Path(tempfile.mkdtemp())
    p = d / "t.csv"
    with p.open("w", newline="") as f:
        csv.writer(f).writerows([["id", "name", "amount"], [1, "a", 10]])
    out = source_columns({"id": "t", "type": "file", "file_type": "delimited_file", "file_path": str(p)})
    assert out["columns"] == ["id", "name", "amount"], out["columns"]
    print("columns.py self-check ok")
