#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import argparse
import unittest

import pandas as pd
import numpy as np
from ingen.utils.utils import KeyValue, KeyValueOrString, compare


class MyTestCase(unittest.TestCase):
    def test_command_line_key_value_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--query_params', nargs='*', action=KeyValue)
        args = parser.parse_args(['--query_params', 'date=12/09/1995', 'table=position'])
        self.assertDictEqual({'date': '12/09/1995', 'table': 'position'}, args.query_params)
        return parser

    def test_key_value_or_string_single_value(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--infile', nargs='*', action=KeyValueOrString)
        args = parser.parse_args(['--infile', 'data.json'])
        self.assertEqual('data.json', args.infile)

    def test_key_value_or_string_key_value_pairs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--infile', nargs='*', action=KeyValueOrString)
        args = parser.parse_args(['--infile', 'source1=data1.json', 'source2=data2.json'])
        self.assertDictEqual({'source1': 'data1.json', 'source2': 'data2.json'}, args.infile)

    def test_compare_equals(self):
        df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        result = compare(df, 'A', ['==', 3])
        expected = pd.Series([False, False, True, False, False])
        pd.testing.assert_series_equal(result, expected)

    def test_compare_greater_than(self):
        df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        result = compare(df, 'A', ['>', 3])
        expected = pd.Series([False, False, False, True, True])
        pd.testing.assert_series_equal(result, expected)

    def test_compare_invalid_column(self):
        df = pd.DataFrame({'A': [1, 2, 3]})
        with self.assertRaises(ValueError) as context:
            compare(df, 'B', ['==', 1])
        self.assertIn("Column B not found in dataframe", str(context.exception))

if __name__ == '__main__':
    unittest.main()
