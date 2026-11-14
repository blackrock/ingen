import unittest

import pandas as pd
import yaml

from ingen.formatters.common_formatters import bucket_formatter, split_column_formatter


class TestFormatterBoundaries(unittest.TestCase):
    def test_bucket_accepts_yaml_boolean_include_right(self):
        config = yaml.safe_load('buckets: [0, 10, 20]\nlabels: [low, high]\ninclude_right: false')
        result = bucket_formatter(pd.DataFrame({'value': [0, 10]}), 'value', config, {})
        self.assertEqual(result['value'].tolist(), ['low', 'high'])

    def test_split_array_preserves_filtered_row_index(self):
        data = pd.DataFrame({'value': [[1, 2], [3, 4]]}, index=[4, 9])
        result = split_column_formatter(data, 'value', {'new_col_names': ['a', 'b']}, {})
        expected = pd.DataFrame({'value': [[1, 2], [3, 4]], 'a': [1, 3], 'b': [2, 4]}, index=[4, 9])
        pd.testing.assert_frame_equal(result, expected)

    def test_split_treats_multicharacter_delimiter_literally(self):
        data = pd.DataFrame({'value': ['one||two', 'three||four']})
        result = split_column_formatter(
            data, 'value', {'new_col_names': ['a', 'b'], 'delimiter': '||'}, {})
        self.assertEqual(result['a'].tolist(), ['one', 'three'])
        self.assertEqual(result['b'].tolist(), ['two', 'four'])
