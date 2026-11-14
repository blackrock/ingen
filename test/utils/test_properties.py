import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ingen.utils.properties import Properties


class TestProperties(unittest.TestCase):
    def test_repeated_construction_preserves_singleton_and_loaded_values(self):
        with patch.object(Properties, '_instance', None), patch.dict(os.environ, {}, clear=True):
            first = Properties()
            first.property_map['loaded'] = 'value'
            second = Properties()
            self.assertIs(second, first)
            self.assertEqual(second.get_property('loaded'), 'value')

    def test_values_can_contain_equals_signs(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'config.properties').write_text(
                'token=YWJj==\nurl=https://example.test/?a=1&b=2\n', encoding='utf-8')
            with patch.object(Properties, '_instance', None), patch.dict(
                    os.environ, {'config_path': directory}), contextlib.redirect_stdout(io.StringIO()):
                properties = Properties()
            self.assertEqual(properties.get_property('token'), 'YWJj==')
            self.assertEqual(properties.get_property('url'), 'https://example.test/?a=1&b=2')
