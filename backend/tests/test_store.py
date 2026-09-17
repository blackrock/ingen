#  Tests for backend/app/store.py
#
#  RunStore persists RunRecords as one JSON file each. These tests pin save/get/round-trip, the
#  missing-id None contract, config filtering, newest-first ordering, and corruption tolerance in
#  list(). Each test uses an isolated temp directory so nothing touches the real .runs store.

import json
import tempfile
import unittest
from pathlib import Path

from backend.app.store import RunStore


class RunStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.store = RunStore(self._tmp.name)

    def _rec(self, run_id, config_id="cfg", started_at="2026-01-01T00:00:00+00:00"):
        return {"runId": run_id, "configId": config_id, "startedAt": started_at, "status": "success"}

    def test_save_and_get_round_trip(self):
        rec = self._rec("run_a")
        self.store.save(rec)
        self.assertEqual(self.store.get("run_a"), rec)

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.store.get("run_nope"))

    def test_list_filters_by_config_id(self):
        self.store.save(self._rec("run_a", config_id="x"))
        self.store.save(self._rec("run_b", config_id="y"))
        ids = {r["runId"] for r in self.store.list(config_id="x")}
        self.assertEqual(ids, {"run_a"})

    def test_list_sorted_newest_first(self):
        self.store.save(self._rec("run_old", started_at="2026-01-01T00:00:00+00:00"))
        self.store.save(self._rec("run_new", started_at="2026-06-01T00:00:00+00:00"))
        order = [r["runId"] for r in self.store.list()]
        self.assertEqual(order, ["run_new", "run_old"])

    def test_list_tolerates_corrupt_files(self):
        self.store.save(self._rec("run_ok"))
        # A truncated/garbage file matching the glob must be skipped, not crash list().
        (Path(self._tmp.name) / "run_bad.json").write_text("{ not valid json", encoding="utf-8")
        ids = {r["runId"] for r in self.store.list()}
        self.assertEqual(ids, {"run_ok"})

    def test_creates_directory_if_missing(self):
        nested = Path(self._tmp.name) / "deep" / "runs"
        store = RunStore(str(nested))
        self.assertTrue(nested.exists())
        store.save(self._rec("run_a"))
        self.assertEqual(json.loads((nested / "run_a.json").read_text())["runId"], "run_a")


if __name__ == "__main__":
    unittest.main()
