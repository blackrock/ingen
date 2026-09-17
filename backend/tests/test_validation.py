#  Tests for backend/app/validation.py
#
#  derive_validation enumerates the column validations configured in the YAML and marks each one's
#  status from the run outcome (failing interface → failed/warning by severity; succeeding → passed).
#  These tests pin that mapping and the summary tallies, including the column-name fallback chain.

import unittest

from backend.app.validation import derive_validation


def _cfg(severity="blocker"):
    return {
        "interfaces": {
            "A": {
                "columns": [
                    {"dest_col_name": "c1", "validations": [{"type": "not_null", "severity": severity}]},
                ]
            }
        }
    }


class DeriveValidation(unittest.TestCase):
    def test_passed_when_interface_succeeds(self):
        rep = derive_validation(_cfg("blocker"), ["A"], failed_interfaces=set())
        self.assertEqual(rep["results"][0]["status"], "passed")
        self.assertEqual(rep["results"][0]["unexpectedCount"], 0)
        self.assertEqual(rep["summary"], {"passed": 1, "failed": 0, "warning": 0, "total": 1})

    def test_non_warning_severity_fails_when_interface_fails(self):
        rep = derive_validation(_cfg("blocker"), ["A"], failed_interfaces={"A"})
        self.assertEqual(rep["results"][0]["status"], "failed")
        self.assertEqual(rep["results"][0]["unexpectedCount"], 1)
        self.assertEqual(rep["summary"]["failed"], 1)

    def test_warning_severity_warns_when_interface_fails(self):
        rep = derive_validation(_cfg("warning"), ["A"], failed_interfaces={"A"})
        self.assertEqual(rep["results"][0]["status"], "warning")
        self.assertEqual(rep["summary"]["warning"], 1)

    def test_column_name_fallback_to_src_then_unnamed(self):
        cfg = {"interfaces": {"A": {"columns": [
            {"src_col_name": "s1", "validations": [{"type": "t"}]},
            {"validations": [{"type": "t"}]},
        ]}}}
        rep = derive_validation(cfg, ["A"], set())
        cols = [r["column"] for r in rep["results"]]
        self.assertEqual(cols, ["s1", "(unnamed)"])

    def test_default_severity_is_warning(self):
        cfg = {"interfaces": {"A": {"columns": [{"dest_col_name": "c", "validations": [{"type": "t"}]}]}}}
        rep = derive_validation(cfg, ["A"], set())
        self.assertEqual(rep["results"][0]["severity"], "warning")

    def test_empty_config_yields_empty_report(self):
        rep = derive_validation({}, [], set())
        self.assertEqual(rep["results"], [])
        self.assertEqual(rep["summary"]["total"], 0)

    def test_interface_without_columns_is_skipped(self):
        rep = derive_validation({"interfaces": {"A": {}}}, ["A"], set())
        self.assertEqual(rep["summary"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
