#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json
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
        mock_json_writer.assert_any_call(df, output_type, {**props, 'path': '../output/file1.json'})
        mock_json_writer.assert_any_call(df, output_type, {**props, 'path': '../output/file2.json'})
        self.assertEqual(mock_json_writer.return_value.write.call_count, 2)

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


class TestWriterListPaths(unittest.TestCase):
    """Real-file tests for list-valued props['path']."""

    def setUp(self) -> None:
        self.df = pd.DataFrame({
            'name': ['Ramesh', 'Suresh', 'Jaya', 'Rekha'],
            'marks': [20, 40, 50, 30]
        })
        self.json_config = {
            'orient': 'records',
            'indent': 2,
            'column_details': {
                'schema': [
                    {'field_name': 'name', 'field_type': 'str'},
                    {'field_name': 'marks', 'field_type': 'str'},
                ],
                'resultant_columns': ['name', 'marks'],
            },
        }

    def test_json_writer_writes_all_listed_paths(self):
        """The legacy 'json' type writes to every path in a list."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, 'a.json'), os.path.join(tmp, 'b.json')]
            props = {'path': paths, 'config': self.json_config}
            InterfaceWriter(self.df, 'json', props, {}).file_writer()
            for path in paths:
                self.assertTrue(os.path.exists(path))
                with open(path) as f:
                    records = json.load(f)
                self.assertEqual(4, len(records))
                self.assertEqual('Ramesh', records[0]['name'])

    def test_add_header_footer_list_path(self):
        """Header/footer are applied to a one-element list path."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, 'out.csv')
            self.df.to_csv(out, ',', index=False)
            InterfaceWriter(self.df, 'delimited_file', {'path': [out]}, {}).add_header_footer('HDR', 'TRL')
            with open(out) as f:
                lines = f.readlines()
            self.assertEqual('HDR', lines[0].strip())
            self.assertEqual('TRL', lines[-1].strip())

    def test_add_header_footer_multi_element_list_path(self):
        """Header/footer are applied to every path in a list."""
        with tempfile.TemporaryDirectory() as tmp:
            paths = [os.path.join(tmp, 'a.csv'), os.path.join(tmp, 'b.csv')]
            for p in paths:
                self.df.to_csv(p, ',', index=False)
            InterfaceWriter(self.df, 'delimited_file', {'path': paths}, {}).add_header_footer('HDR', 'TRL')
            for path in paths:
                with open(path) as f:
                    lines = f.readlines()
                self.assertEqual('HDR', lines[0].strip())
                self.assertEqual('TRL', lines[-1].strip())

    def test_add_header_footer_str_path(self):
        """A plain string path still works (backward compatible)."""
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, 'out.csv')
            self.df.to_csv(out, ',', index=False)
            InterfaceWriter(self.df, 'delimited_file', {'path': out}, {}).add_header_footer('HDR', 'TRL')
            with open(out) as f:
                lines = f.readlines()
            self.assertEqual('HDR', lines[0].strip())
            self.assertEqual('TRL', lines[-1].strip())


if __name__ == '__main__':
    unittest.main()
