import os
import unittest
from unittest.mock import patch

from ingen.utils.parse_utils import ENVIRONMENT_VAR_PATTERN
from ingen.utils.parse_utils import get_environment_value
from ingen.utils.parse_utils import var_starts_with


class TestParseUtils(unittest.TestCase):

    def test_var_starts_with_pattern_when_matches(self):
        self.assertTrue(var_starts_with('$$VAR', ENVIRONMENT_VAR_PATTERN))

    def test_var_starts_with_pattern_when_does_not_matches(self):
        self.assertFalse(var_starts_with('VAR', ENVIRONMENT_VAR_PATTERN))

    @patch.dict(os.environ, {'FILE_SOURCE': 'test/file/path/'})
    def test_get_environment_value_when_value_present(self):
        self.assertEqual('test/file/path/', get_environment_value('FILE_SOURCE'))

    @patch.dict(os.environ, {})
    def test_get_environment_value_when_value_present(self):
        self.assertEqual(None, get_environment_value('FILE_SOURCE'))


if __name__ == "__main__":
    unittest.main()
