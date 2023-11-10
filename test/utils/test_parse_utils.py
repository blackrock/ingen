#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os
import unittest
from unittest.mock import patch

ENVIRONMENT_VAR_PATTERN = "$$"


class TestParseUtils(unittest.TestCase):

    def test_var_starts_with_pattern_when_matches(self):
        self.assertTrue('$$VAR'.startswith(ENVIRONMENT_VAR_PATTERN))

    def test_var_starts_with_pattern_when_does_not_matches(self):
        self.assertFalse('VAR'.startswith(ENVIRONMENT_VAR_PATTERN))

    @patch.dict(os.environ, {'FILE_SOURCE': 'test/file/path/'})
    def test_get_environment_value_when_value_present(self):
        self.assertEqual('test/file/path/', os.getenv('FILE_SOURCE'))

    @patch.dict(os.environ, {})
    def test_get_environment_value_when_value_present(self):
        self.assertEqual(None, os.getenv('FILE_SOURCE'))


if __name__ == "__main__":
    unittest.main()
