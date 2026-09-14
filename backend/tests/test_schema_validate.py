#  Tests for backend/app/schema_validate.py
#
#  validate_yaml does structural/cross-reference checks (no execution) and returns { valid, issues }.
#  These tests pin every issue code.

import unittest

from backend.app.schema_validate import validate_yaml


def codes(result):
    return {i["code"] for i in result["issues"]}


class ValidateYaml(unittest.TestCase):
    def test_valid_config(self):
        res = validate_yaml("sources:\n  - id: s1\n    type: file\ninterfaces:\n  A:\n    sources: [s1]\n")
        self.assertTrue(res["valid"])
        self.assertNotIn("UNKNOWN_SOURCE_REF", codes(res))

    def test_invalid_yaml_is_parse_error(self):
        res = validate_yaml("a: b: c:\n  - : :")
        self.assertFalse(res["valid"])
        self.assertEqual(codes(res), {"PARSE_ERROR"})

    def test_non_mapping_top_level(self):
        res = validate_yaml("- one\n- two\n")
        self.assertFalse(res["valid"])
        self.assertEqual(codes(res), {"PARSE_ERROR"})

    def test_no_interfaces_warns_but_is_valid(self):
        res = validate_yaml("sources:\n  - id: s1\n    type: file\n")
        self.assertTrue(res["valid"])
        self.assertIn("NO_INTERFACES", codes(res))

    def test_source_missing_id(self):
        res = validate_yaml("sources:\n  - type: file\ninterfaces:\n  A: {}\n")
        self.assertFalse(res["valid"])
        self.assertIn("SOURCE_NO_ID", codes(res))

    def test_unknown_source_type(self):
        res = validate_yaml("sources:\n  - id: s1\n    type: ftp\ninterfaces:\n  A: {}\n")
        self.assertFalse(res["valid"])
        self.assertIn("UNKNOWN_SOURCE_TYPE", codes(res))

    def test_unknown_source_reference(self):
        res = validate_yaml("sources:\n  - id: s1\n    type: file\ninterfaces:\n  A:\n    sources: [s2]\n")
        self.assertFalse(res["valid"])
        self.assertIn("UNKNOWN_SOURCE_REF", codes(res))

    def test_all_supported_source_types_accepted(self):
        for t in ("file", "mysql", "api", "json"):
            res = validate_yaml(f"sources:\n  - id: s1\n    type: {t}\ninterfaces:\n  A: {{}}\n")
            self.assertNotIn("UNKNOWN_SOURCE_TYPE", codes(res), t)


if __name__ == "__main__":
    unittest.main()
