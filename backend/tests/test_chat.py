#  Tests for backend/app/chat.py — the model-free pieces (op vocabulary + filter).
#  We do NOT load the HF model here; we pin the contract that guards against the vocabulary drift
#  the code review flagged (LLM vocabulary must equal what frontend/src/models/applyIntent.js runs).

import unittest

from backend.app.chat import _filter_ops, _extract_json, _build_user_content, _PREFILL, _YAML_CAP, OPS


class FilterOps(unittest.TestCase):
    def test_keeps_supported_ops(self):
        ops = [{"op": "remove_source", "name": "s"}, {"op": "explain"}]
        self.assertEqual(_filter_ops(ops), ops)

    def test_drops_unknown_and_malformed(self):
        self.assertEqual(_filter_ops([{"op": "nope"}, "x", 3, {}]), [])

    def test_non_list_is_empty(self):
        self.assertEqual(_filter_ops(None), [])

    def test_vocabulary_matches_executor(self):
        # If this fails, chat.py and applyIntent.js have drifted again. Re-sync them.
        self.assertEqual(OPS, {
            "add_columns", "remove_column", "rename_column",
            "add_source", "remove_source",
            "add_transform", "remove_transform",
            "add_filter", "set_output", "explain", "none",
        })


class ExtractJson(unittest.TestCase):
    def test_prefill_stitching(self):
        # interpret() prepends _PREFILL to the model continuation before parsing.
        raw = 'hi there", "ops": []}'
        self.assertEqual(
            _extract_json(_PREFILL + raw), {"reply": "hi there", "ops": []}
        )

    def test_fenced_nested_ops_not_truncated(self):
        # The greedy fence regex must not cut at the first } inside an op object.
        text = (
            '```json\n{"reply": "ok", "ops": [{"op": "add_columns", "cols": ["a"]}]}\n```'
        )
        self.assertEqual(
            _extract_json(text),
            {"reply": "ok", "ops": [{"op": "add_columns", "cols": ["a"]}]},
        )

    def test_trailing_prose_after_json(self):
        text = '{"reply": "done", "ops": []}\nHope that helps!'
        self.assertEqual(_extract_json(text), {"reply": "done", "ops": []})

    def test_garbage_is_empty(self):
        self.assertEqual(_extract_json("not json at all"), {})


class BuildUserContent(unittest.TestCase):
    def test_yaml_truncated(self):
        big = "x: 1\n" * 2000
        out = _build_user_content("go", ["id"], big, "main")
        self.assertIn("(truncated)", out)
        self.assertLessEqual(len(out), _YAML_CAP + 500)  # cap + framing, not the full YAML

    def test_history_folded_in_as_text(self):
        history = [{"role": "user", "content": "add a"}, {"role": "assistant", "content": "done"}]
        out = _build_user_content("now add b", [], "", "main", history)
        self.assertIn("Recent conversation:", out)
        self.assertIn("user: add a", out)
        self.assertIn("Request: now add b", out)


if __name__ == "__main__":
    unittest.main()
