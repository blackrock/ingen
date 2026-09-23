#  Tests for backend/app/files.py — upload parsing is by content, not by an extension allowlist.

import os
import tempfile
import unittest

from backend.app.files import save_and_parse


class SaveAndParse(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)  # files.py writes under a relative Data/

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_mainframe_style_extension_is_sniffed_as_delimited(self):
        body = b"acct|cusip|qty\nA1|037833100|100\nA2|594918104|200\n"
        meta = save_and_parse("OpenLot_10202020.mlm.1", body)
        self.assertEqual(meta["columns"], ["acct", "cusip", "qty"])
        self.assertEqual(meta["preview"][0], ["A1", "037833100", "100"])

    def test_unparseable_file_is_rejected_and_not_kept(self):
        with self.assertRaises(ValueError):
            save_and_parse("empty.dat", b"")
        self.assertFalse(os.path.exists(os.path.join("Data", "empty.dat")))


if __name__ == "__main__":
    unittest.main()
