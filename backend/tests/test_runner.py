#  Tests for backend/app/runner.py
#
#  The runner is the riskiest backend module: it builds the InGen CLI command and infers a structured
#  RunRecord from unstructured log text. These tests pin (a) the A3 param-emission fix — multiple
#  query/override params must ride a SINGLE flag, not be repeated — and (b) the status/stage/log
#  derivation across success / partial / failure / crash, all via an injected fake executor so no real
#  InGen subprocess runs.

import unittest

from backend.app.runner import (
    _as_param_pairs,
    _furthest_stage,
    build_run_record,
    execute_run,
)


def _record(output, exit_code, config, overrides=None):
    return build_run_record(
        config_id="cfg", config_name="cfg", overrides=overrides or {},
        started_at="2026-01-01T00:00:00+00:00", finished_at="2026-01-01T00:00:01+00:00",
        duration_ms=1000, exit_code=exit_code, output=output, config=config,
    )


class AsParamPairs(unittest.TestCase):
    def test_empty_and_none(self):
        self.assertEqual(_as_param_pairs(None), [])
        self.assertEqual(_as_param_pairs({}), [])

    def test_renders_all_pairs(self):
        self.assertEqual(_as_param_pairs({"a": 1, "b": "x"}), ["a=1", "b=x"])

    def test_value_with_equals_is_preserved(self):
        # InGen splits on the first '=', so a value containing '=' must survive untouched here.
        self.assertEqual(_as_param_pairs({"q": "col=1"}), ["q=col=1"])


class ExecuteRunCommand(unittest.TestCase):
    """The A3 regression: every override pair must be passed under ONE flag occurrence."""

    def setUp(self):
        self.captured = {}

        def fake_executor(cmd, cwd):
            self.captured["cmd"] = cmd
            self.captured["cwd"] = cwd
            return 0, "Successfully generated interface 'A'"

        self.executor = fake_executor
        self.config = {"interfaces": {"A": {}}}

    def _run(self, overrides):
        return execute_run("interfaces: {A: {}}\n", overrides, self.config,
                           workdir="/work", executor=self.executor)

    def test_query_params_single_flag_with_all_pairs(self):
        self._run({"query_params": {"a": "1", "b": "2"}})
        cmd = self.captured["cmd"]
        # Exactly one '--query_params', immediately followed by both pairs.
        self.assertEqual(cmd.count("--query_params"), 1)
        idx = cmd.index("--query_params")
        self.assertEqual(cmd[idx + 1:idx + 3], ["a=1", "b=2"])

    def test_override_params_single_flag_with_all_pairs(self):
        self._run({"override_params": {"x": "9", "y": "8"}})
        cmd = self.captured["cmd"]
        self.assertEqual(cmd.count("--override_params"), 1)
        idx = cmd.index("--override_params")
        self.assertEqual(cmd[idx + 1:idx + 3], ["x=9", "y=8"])

    def test_omits_flags_when_no_params(self):
        self._run({})
        cmd = self.captured["cmd"]
        self.assertNotIn("--query_params", cmd)
        self.assertNotIn("--override_params", cmd)

    def test_interfaces_and_run_date_are_passed(self):
        self._run({"run_date": "2026-06-16", "interfaces": ["A", "B"]})
        cmd = self.captured["cmd"]
        self.assertIn("2026-06-16", cmd)
        idx = cmd.index("--interfaces")
        self.assertEqual(cmd[idx + 1], "A,B")
        self.assertEqual(self.captured["cwd"], "/work")

    def test_executor_exception_is_captured_as_failure(self):
        def boom(cmd, cwd):
            raise RuntimeError("subprocess exploded")

        record = execute_run("interfaces: {A: {}}\n", {}, self.config,
                             workdir="/work", executor=boom)
        # A crash before any per-interface marker → all requested interfaces marked failed.
        self.assertEqual(record["status"], "failed")
        self.assertTrue(any("exploded" in ln["message"] for ln in record["logs"]))


class BuildRunRecordStatus(unittest.TestCase):
    def test_success(self):
        rec = _record("Generating interface 'A'\nSuccessfully generated interface 'A'", 0,
                      {"interfaces": {"A": {}}})
        self.assertEqual(rec["status"], "success")
        self.assertTrue(all(s["status"] == "ok" for s in rec["stages"]))

    def test_all_failed(self):
        rec = _record("Failed to generate interface file for A", 0, {"interfaces": {"A": {}}})
        self.assertEqual(rec["status"], "failed")

    def test_partial(self):
        out = ("Generating interface 'A'\nSuccessfully generated interface 'A'\n"
               "Generating interface 'B'\nFailed to generate interface file for B")
        rec = _record(out, 0, {"interfaces": {"A": {}, "B": {}}})
        self.assertEqual(rec["status"], "partial")

    def test_crash_before_markers_fails_all_requested(self):
        rec = _record("Traceback (most recent call last): boom", 1,
                      {"interfaces": {"A": {}, "B": {}}})
        self.assertEqual(rec["status"], "failed")
        self.assertEqual({s["interface"] for s in rec["stages"]}, {"A", "B"})

    def test_logs_capture_level(self):
        rec = _record("Generating interface 'A'\n2026-01-01 00:00:00 - root - ERROR - boom\n"
                      "Successfully generated interface 'A'",
                      0, {"interfaces": {"A": {}}})
        levels = {ln["level"] for ln in rec["logs"]}
        self.assertIn("error", levels)

    def test_stage_set_includes_post_process_when_configured(self):
        rec = _record("Generating interface 'A'\nSuccessfully generated interface 'A'", 0,
                      {"interfaces": {"A": {"post_processing": [{"type": "pivot"}]}}})
        stages = {s["stage"] for s in rec["stages"] if s["interface"] == "A"}
        self.assertIn("post_process", stages)


class LevelOf(unittest.TestCase):
    def test_level_of_uses_log_prefix_not_substring(self):
        from backend.app.runner import _level_of
        # A data value containing "error" must NOT be flagged as an error.
        self.assertEqual(_level_of("2026-01-01 00:00:00 - root - INFO - balance error column loaded"), "info")
        self.assertEqual(_level_of("2026-01-01 00:00:00 - root - ERROR - boom"), "error")
        self.assertEqual(_level_of("2026-01-01 00:00:00 - py.warnings - WARNING - FutureWarning"), "warn")
        self.assertEqual(_level_of("Traceback (most recent call last):"), "error")


class FurthestStage(unittest.TestCase):
    def test_reaches_read_when_no_markers(self):
        self.assertEqual(_furthest_stage("Generating interface 'A'", "A"), "read")

    def test_reaches_pre_process(self):
        out = "Generating interface 'A'\nStarting pre-processing now"
        self.assertEqual(_furthest_stage(out, "A"), "pre_process")

    def test_marker_isolated_to_interface_slice(self):
        # B's pre-processing marker must not bleed into A's slice.
        out = ("Generating interface 'A'\n"
               "Generating interface 'B'\nStarting pre-processing for B")
        self.assertEqual(_furthest_stage(out, "A"), "read")

    def test_failed_interface_marks_reached_stage_failed_rest_skipped(self):
        out = "Generating interface 'A'\nStarting pre-processing\nFailed to generate interface file for A"
        rec = _record(out, 0, {"interfaces": {"A": {}}})
        by_stage = {s["stage"]: s["status"] for s in rec["stages"]}
        self.assertEqual(by_stage["read"], "ok")
        self.assertEqual(by_stage["pre_process"], "failed")
        self.assertEqual(by_stage["format"], "skipped")
        self.assertEqual(by_stage["write"], "skipped")


if __name__ == "__main__":
    unittest.main()
