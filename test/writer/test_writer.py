#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import csv
import io
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, mock_open

import pandas as pd

from ingen.writer.writer import InterfaceWriter


class TestWriter(unittest.TestCase):

    def test_csv_with_delimited_header(self):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv

        output_type = 'delimited_file'
        props = {
            'delimiter': ',',
            'path': r'../output/positions.csv',
            'header': {'type': 'delimited_result_header',
                       'function': [{
                           'constant': "HMOCK"
                       }]},
            'footer': {'type': 'delimited_result_header',
                       'function': [{
                           'constant': "HMOCK"
                       }]},
        }

        writer = InterfaceWriter(df, output_type, props, {})
        writer.write()
        mock_to_csv.assert_called_with(props['path'], props['delimiter'], index=InterfaceWriter.SHOW_DATAFRAME_INDEX, encoding='utf-8')

    def test_file_with_delimited_header_and_footer(self):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv

        output_type = 'delimited_file'
        props = {
            'delimiter': ',',
            'path': r'../output/positions.csv',
            'header': {'type': 'delimited_result_header',
                       'function': [{
                           'constant': "HMOCK"
                       }]},
            'footer': {
                'type': 'custom',
                'function': [{
                    'constant': "HMOCK"
                }]
            }
        }
        header = props['header']['type']
        footer = props['footer']['type']
        config_file_path = props['path']
        path = os.path.join(config_file_path)
        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()
        mock_to_csv.assert_called_with(props['path'], props['delimiter'], index=InterfaceWriter.SHOW_DATAFRAME_INDEX, encoding='utf-8')

        with patch('ingen.writer.writer.open', mock_open()) as mocked_file:
            writer.add_header_footer(header, footer)

            # assert if opened file on write mode 'a'
            mocked_file.assert_called_with(path, 'r+', encoding='utf-8')

            # assert if write(content) was called from the file opened
            # in another words, assert if the specific content was written in file
            mocked_file().write.assert_called_with(footer)

    def test_without_delimited_header_csv(self):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv

        output_type = 'delimited_file'
        props = {
            'path': '../output/positions.csv',
            'header': {
                'type': 'custom',
                'function': [{
                    'constant': "HMOCK"
                }]
            },
            'footer': {
                'type': 'custom',
                'function': [{
                    'constant': "HMOCK"
                }]
            }
        }

        header = props['header']['type']
        footer = props['footer']['type']
        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()
        mock_to_csv.assert_called_with(props['path'], ',', header=False, index=InterfaceWriter.SHOW_DATAFRAME_INDEX, encoding='utf-8')
        config_file_path = props['path']
        path = os.path.join(config_file_path)

        with patch('ingen.writer.writer.open', mock_open()) as mocked_file:
            writer.add_header_footer(header, footer)
            mocked_file.assert_called_with(path, 'r+', encoding='utf-8')
            mocked_file().write.assert_called_with(header)
            mocked_file().write.assert_called_with(footer)

    def test_excel_file_with_delimited_header(self):
        df = Mock()
        mock_to_excel = Mock()
        df.to_excel = mock_to_excel

        output_type = 'excel'
        props = {
            'path': '../output/positions.xlsx',
            'header': {'type': 'delimited_result_header',
                       'function': [{
                           'constant': "HMOCK"
                       }]}

        }

        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()
        mock_to_excel.assert_called_with(props['path'], index=InterfaceWriter.SHOW_DATAFRAME_INDEX)

    def test_excel_file_without_delimited_header(self):
        df = Mock()
        mock_to_excel = Mock()
        df.to_excel = mock_to_excel

        output_type = 'excel'
        props = {
            'path': '../output/positions.xlsx',
            'header': {'type': 'custom',
                       'function': [{
                           'constant': "HMOCK"
                       }]}

        }

        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()
        mock_to_excel.assert_called_with(props['path'], header=False, index=InterfaceWriter.SHOW_DATAFRAME_INDEX)

    def test_get_header_string(self):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv

        output_type = 'delimited_file'
        props = {
            'path': '../output/positions.csv',
            'header': {
                'type': 'custom',
                'function': [{
                    'constant': "HMOCK"
                }]
            },
            'footer': {
                'type': 'custom',
                'function': [{
                    'constant': "TMOCK"
                }]
            }
        }
        writer = InterfaceWriter(df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        actual_header = writer.get_header()
        self.assertEqual(actual_header, "HMOCK")

    def test_get_footer_string(self):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv

        output_type = 'delimited_file'
        props = {
            'path': '../output/positions.csv',
            'header': {
                'type': 'custom',
                'function': [{
                    'constant': "HMOCK"
                }]
            },
            'footer': {
                'type': 'custom',
                'function': [{
                    'constant': "TMOCK"
                }]
            }
        }
        writer = InterfaceWriter(df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        actual_footer = writer.get_footer()
        self.assertEqual(actual_footer, "TMOCK")

    @patch('ingen.writer.writer.get_custom_value')
    def test_get_custom_value(self, mock_user_defined_value):
        df = Mock()
        mock_to_csv = Mock()
        df.to_csv = mock_to_csv
        output_type = 'delimited_file'
        props = {
            'file_type': 'csv',
            'path': '../output/positions.xlsx',
            'header':
                {'type': 'custom',
                 'function': [
                     {'constant': 'H'},
                     {'filler': 20},
                     {'row_count': 3}
                 ]},
            'footer': {
                'type': 'custom',
                'function': [
                    {'constant': 'T'},
                    {'filler': 20}
                ]
            }
        }
        writer = InterfaceWriter(df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        writer.custom_function(props['header']['function'])
        writer.custom_function(props['footer']['function'])
        mock_user_defined_value.assert_called()

    @patch('ingen.writer.writer.JSONWriter')
    def test_json_writer_is_called(self, mock_json_writer):
        config = {
            'type': 'json_writer',
            'props': {
                'convertor': 'single',
                'convertor_props': {
                    'orient': 'records',
                    'indent': 4,
                    'column_details': {
                        'schema': [
                            {
                                'field_name': 'col_name',
                                'field_type': 'str'
                            }
                        ]
                    },
                    'resultant_columns': ['col_name']
                },
                'destination': 'file',
                'destination_props': {
                    'path': '../fake/file.json'
                }
            }
        }
        mock_writer = Mock()
        mock_json_writer.return_value = mock_writer

        writer = InterfaceWriter(pd.DataFrame, 'json_writer', config, {})
        writer.write()

        mock_writer.write.assert_called()

    @patch('ingen.writer.writer.DataFrameWriter')
    def test_df_writer_is_called(self, mock_df_writer):
        df = Mock()
        output_type = 'rawdatastore'

        props = {'id': 'DF1'}

        mock_writer = Mock()
        mock_df_writer.return_value = mock_writer
        writer = InterfaceWriter(df, output_type, props, {})
        writer.write()
        mock_writer.write.assert_called()

    @patch('ingen.writer.writer.OldJSONWriter')
    def test_file_writer_multiple_paths(self, mock_json_writer):
        df = Mock()
        output_type = 'json'
        props = {
            'path': ['../output/file1.json', '../output/file2.json'],
            'type': 'json'
        }

        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()

        self.assertEqual(mock_json_writer.call_count, 2)
        mock_json_writer.assert_any_call(df, output_type, props)
        mock_json_writer.return_value.write_assert_called()

    @patch('ingen.writer.writer.OldJSONWriter')
    def test_file_writer_single_path(self, mock_json_writer):
        # Arrange
        df = Mock()
        output_type = 'json'
        props = {
            'path': '../output/file1.json',  # path is now a string, not a list
            'type': 'json'
        }

        writer = InterfaceWriter(df, output_type, props, {})
        writer.file_writer()

        self.assertEqual(mock_json_writer.call_count, 1)
        mock_json_writer.assert_any_call(df, output_type, props)
        mock_json_writer.return_value.write.assert_called()

    def test_csv_quote_all_with_header(self):
        df = Mock()
        df.to_csv = Mock()

        props = {
            'delimiter': ',',
            'path': '../output/positions.csv',
            'header': {'type': 'delimited_result_header'},
            'quote_all': True,
        }

        writer = InterfaceWriter(df, 'delimited_file', props, {})
        writer.write()
        df.to_csv.assert_called_with(props['path'], ',', index=InterfaceWriter.SHOW_DATAFRAME_INDEX,
                                     encoding='utf-8', quoting=csv.QUOTE_ALL)

    def test_csv_quote_all_without_header(self):
        df = Mock()
        df.to_csv = Mock()

        props = {
            'path': '../output/positions.csv',
            'quote_all': True,
        }

        writer = InterfaceWriter(df, 'delimited_file', props, {})
        writer.write()
        df.to_csv.assert_called_with(props['path'], ',', header=False,
                                     index=InterfaceWriter.SHOW_DATAFRAME_INDEX,
                                     encoding='utf-8', quoting=csv.QUOTE_ALL)

    def test_csv_quote_all_accepts_string_true(self):
        for value in ('true', 'True', ' TRUE '):
            with self.subTest(value=value):
                df = Mock()
                df.to_csv = Mock()

                props = {
                    'delimiter': ',',
                    'path': '../output/positions.csv',
                    'header': {'type': 'delimited_result_header'},
                    'quote_all': value,
                }

                writer = InterfaceWriter(df, 'delimited_file', props, {})
                writer.write()
                self.assertEqual(df.to_csv.call_args.kwargs['quoting'], csv.QUOTE_ALL)

    def test_csv_quote_all_disabled_keeps_default_call(self):
        for value in (False, 'false', None, 'key-absent'):
            with self.subTest(value=value):
                df = Mock()
                df.to_csv = Mock()

                props = {
                    'delimiter': ',',
                    'path': '../output/positions.csv',
                    'header': {'type': 'delimited_result_header'},
                }
                if value != 'key-absent':
                    props['quote_all'] = value

                writer = InterfaceWriter(df, 'delimited_file', props, {})
                writer.write()
                df.to_csv.assert_called_with(props['path'], ',',
                                             index=InterfaceWriter.SHOW_DATAFRAME_INDEX,
                                             encoding='utf-8')
                self.assertNotIn('quoting', df.to_csv.call_args.kwargs)

    def test_csv_default_quoting_output_unchanged(self):
        df = pd.DataFrame({
            'name': ['Growth, Balanced', 'He said "hi"',
                     '<b>bold</b> &amp; <a href="x">link</a>', 'line1\nline2',
                     "Zoë O'Brien", None],
            'amount': [1, 2, 3, 4, 5, 6],
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.csv')
            props = {
                'delimiter': ',',
                'path': path,
                'header': {'type': 'delimited_result_header'},
            }
            InterfaceWriter(df, 'delimited_file', props, {}).write()
            with open(path, encoding='utf-8') as f:
                text = f.read()
        self.assertEqual(
            text,
            'name,amount\n"Growth, Balanced",1\n"He said ""hi""",2\n'
            '"<b>bold</b> &amp; <a href=""x"">link</a>",3\n"line1\nline2",4\n'
            "Zoë O'Brien,5\n,6\n")

    def test_csv_quote_all_output(self):
        df = pd.DataFrame({
            'name': ['Growth, Balanced', 'He said "hi"',
                     '<b>bold</b> &amp; <a href="x">link</a>', 'line1\nline2',
                     "Zoë O'Brien", None],
            'amount': [1, 2, 3, 4, 5, 6],
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.csv')
            props = {
                'delimiter': ',',
                'path': path,
                'header': {'type': 'delimited_result_header'},
                'quote_all': True,
            }
            InterfaceWriter(df, 'delimited_file', props, {}).write()
            with open(path, encoding='utf-8') as f:
                text = f.read()
        self.assertEqual(
            text,
            '"name","amount"\n"Growth, Balanced","1"\n"He said ""hi""","2"\n'
            '"<b>bold</b> &amp; <a href=""x"">link</a>","3"\n"line1\nline2","4"\n'
            '"Zoë O\'Brien","5"\n"","6"\n')

    def test_csv_quote_all_round_trips_values(self):
        df = pd.DataFrame({
            'name': ['Growth, Balanced', 'He said "hi"',
                     '<b>bold</b> &amp; <a href="x">link</a>', 'line1\nline2',
                     "Zoë O'Brien", None],
            'amount': [1, 2, 3, 4, 5, 6],
        })
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.csv')
            props = {
                'delimiter': ',',
                'path': path,
                'header': {'type': 'delimited_result_header'},
                'quote_all': True,
            }
            InterfaceWriter(df, 'delimited_file', props, {}).write()
            with open(path, encoding='utf-8') as f:
                text = f.read()
        rows = list(csv.reader(io.StringIO(text)))
        self.assertEqual(rows, [
            ['name', 'amount'],
            ['Growth, Balanced', '1'],
            ['He said "hi"', '2'],
            ['<b>bold</b> &amp; <a href="x">link</a>', '3'],
            ['line1\nline2', '4'],
            ["Zoë O'Brien", '5'],
            ['', '6'],
        ])

if __name__ == '__main__':
    unittest.main()
