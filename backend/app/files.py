#  InGen wrapper — file upload + column/preview parsing (pure logic, no FastAPI import).
#
#  Saves an uploaded data file under repo-root Data/, parses its header + a few sample rows with
#  pandas (already a dependency via InGen), and caches the parsed result keyed by content hash so a
#  re-upload of the same bytes returns instantly without re-reading.

import csv
import hashlib
import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path("Data")
CACHE_DIR = DATA_DIR / ".cache"
PREVIEW_ROWS = 10
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB — trusted-dev guard against accidental OOM


def _parse(path: Path, n=PREVIEW_ROWS):
    """Columns + first n rows, dispatched on extension. Defaults to delimited (csv/tsv/txt)."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, nrows=n)
    elif suffix == ".json":
        df = pd.read_json(path).head(n)
    else:
        # Sniff only among real delimiters: an unconstrained sniff (pandas sep=None) happily picks a
        # letter like "c" on short samples.
        with open(path, newline="", encoding="utf-8", errors="replace") as fh:
            sample = fh.read(64 * 1024)
        try:
            sep = csv.Sniffer().sniff(sample, delimiters=",|;\t").delimiter
        except csv.Error:
            sep = ","
        df = pd.read_csv(path, nrows=n, sep=sep, dtype=str, keep_default_na=False)  # raw text: keep leading zeros
    cols = [str(c) for c in df.columns]
    preview = df.fillna("").astype(str).values.tolist()
    return cols, preview


def save_and_parse(filename: str, content: bytes) -> dict:
    """Persist to Data/<filename>, parse, cache by content hash. Returns
    {file_path, columns, preview, cached}."""
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File too large ({len(content)} bytes; max {MAX_UPLOAD_BYTES}).")
    DATA_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    digest = hashlib.sha256(content).hexdigest()[:16]
    cache_file = CACHE_DIR / f"{digest}.json"
    if cache_file.exists():
        meta = json.loads(cache_file.read_text())
        meta["cached"] = True
        return meta

    dest = DATA_DIR / Path(filename).name  # ponytail: strip any path components from the client name
    dest.write_bytes(content)
    # Any extension is accepted (feeds like OpenLot_10202020.mlm.1 are plain delimited text); what
    # isn't Excel/JSON is sniffed as delimited, and a file that doesn't parse is rejected.
    try:
        cols, preview = _parse(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise ValueError(f"Couldn't read '{dest.name}' as a delimited, Excel or JSON file: {exc}") from exc
    meta = {"file_path": dest.as_posix(), "columns": cols, "preview": preview, "cached": False}
    cache_file.write_text(json.dumps(meta))
    return meta


if __name__ == "__main__":
    # Self-check: parse a tiny CSV and confirm caching kicks in on identical bytes.
    sample = b"id,name,amount\n1,a,10\n2,b,20\n"
    a = save_and_parse("ponytail_selfcheck.csv", sample)
    assert a["columns"] == ["id", "name", "amount"], a["columns"]
    assert a["preview"][0] == ["1", "a", "10"], a["preview"]
    assert a["cached"] is False
    b = save_and_parse("ponytail_selfcheck_other_name.csv", sample)
    assert b["cached"] is True, "identical bytes should hit cache"
    print("files.py self-check ok")
