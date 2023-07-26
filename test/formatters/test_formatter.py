import unittest
from unittest.mock import patch

import pandas as pd

from ingen.formatters.formatter import Formatter


class TestFormatter(unittest.TestCase):
    def test_formatter_creates_an_id_col_map(self):
        columns = [
            {
                'src_col_name': 'start_date',
                'dest_col_name': 'START DATE'
            },
            {
                'src_col_name': 'price',
                'dest_col_name': 'PRICE'
            }
        ]
        df = pd.DataFrame({'start_date': [], 'price': []})
        expected_map = {
            'start_date': 'START DATE',
            'price': 'PRICE'
        }
        formatter = Formatter(df, columns, {})
        self.assertDictEqual(expected_map, formatter._id_name_map)

    def test_default_column_names(self):
        df = pd.DataFrame({'price': [], 'ticket': []})
        columns = [{'src_col_name': 'price'}, {'src_col_name': 'ticker'}]
        expected_map = {
            'price': 'price',
            'ticker': 'ticker'
        }
        formatter = Formatter(df, columns, {})
        self.assertDictEqual(expected_map, formatter._id_name_map)

    def test_default_name_formatter(self):
        df = pd.DataFrame({'price': [], 'ticker': []})
        columns = [{'src_col_name': 'price'}, {'src_col_name': 'ticker'}]
        formatter = Formatter(df, columns, {})
        expected_labels = list(formatter._id_name_map.values())
        formatter.apply_format()
        self.assertListEqual(expected_labels, list(df.columns))

    @patch('ingen.formatters.formatter.get_formatter_from_type')
    def test_get_formatter_func_is_called(self, mock_get_formatter):
        df = pd.DataFrame({'date': ['09-09-2020', '10-09-2020']})
        columns = [
            {
                'src_col_name': 'date',
                'formatters': [
                    {
                        'type': 'date',
                        'format': "%m/%d/%y"
                    }
                ]
            }
        ]

        formatter = Formatter(df, columns, {})
        formatter.apply_format()
        mock_get_formatter.assert_called()

    @patch('ingen.formatters.formatter.column_filter')
    def test_column_filter_is_called(self, mock_column_filter):
        dataframe = pd.DataFrame({'date': ['09092020', '10092020']})
        columns = [
            {
                'src_col_name': 'date',
                'formatters': [
                    {
                        'type': 'date',
                        'format': {"src": "%d%m%Y", "des": "%Y-%m-%d"}
                    }
                ]
            }
        ]
        column_names = [col['src_col_name'] for col in columns]
        formatter = Formatter(dataframe, columns, {})
        formatter.apply_format()
        mock_column_filter.assert_called_with(dataframe, column_names)


if __name__ == '__main__':
    unittest.main()
