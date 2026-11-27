#  Tests for backend/app/columns.py
#
#  source_columns builds an ingen source and returns its column names. Covers the file path and the
#  bad-input guard; SQL/API need live connections so they're out of scope for a unit test.

import csv
import tempfile
import unittest
from pathlib import Path

from backend.app.columns import source_columns


class SourceColumns(unittest.TestCase):
    def test_file_source_returns_header(self):
        d = Path(tempfile.mkdtemp())
        p = d / "t.csv"
        with p.open("w", newline="") as f:
            csv.writer(f).writerows([["id", "name", "amount"], [1, "a", 10]])
        out = source_columns({"id": "t", "type": "file", "file_type": "delimited_file", "file_path": str(p)})
        self.assertEqual(out["columns"], ["id", "name", "amount"])

    def test_missing_type_raises(self):
        with self.assertRaises(ValueError):
            source_columns({"id": "x"})


if __name__ == "__main__":
    unittest.main()
