#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os
from datetime import datetime

import pandas as pd

from ingen.writer.writer import InterfaceWriter


class TestWriter:

    def test_csv_with_delimited_header(self):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, path, delimiter, index):
                self.to_csv_calls.append((path, delimiter, index))

        mock_df = MockDataFrame()

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

        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.write()
        assert mock_df.to_csv_calls == [(props['path'], props['delimiter'], InterfaceWriter.SHOW_DATAFRAME_INDEX)]

    def test_file_with_delimited_header_and_footer(self, monkeypatch):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, path, delimiter, index):
                self.to_csv_calls.append((path, delimiter, index))

        mock_df = MockDataFrame()

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
        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()
        assert mock_df.to_csv_calls == [(props['path'], props['delimiter'], InterfaceWriter.SHOW_DATAFRAME_INDEX)]

        class MockFile:
            def __init__(self):
                self.write_calls = []
                self.content = "existing content\n"
            
            def write(self, content):
                self.write_calls.append(content)
            
            def writelines(self, lines):
                self.write_calls.append(lines)
            
            def readlines(self):
                return [self.content]
            
            def read(self):
                return self.content
            
            def seek(self, pos):
                pass
            
            def truncate(self):
                pass
            
            def close(self):
                pass
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass

        mock_file = MockFile()
        
        def mock_open_func(file_path, mode):
            assert file_path == path
            assert mode == 'r+'
            return mock_file
        
        monkeypatch.setattr("builtins.open", mock_open_func)
        
        writer.add_header_footer(header, footer)
        assert footer in mock_file.write_calls

    def test_without_delimited_header_csv(self, monkeypatch):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, path, delimiter, header, index):
                self.to_csv_calls.append((path, delimiter, header, index))

        mock_df = MockDataFrame()

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
        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()
        assert mock_df.to_csv_calls == [(props['path'], ',', False, InterfaceWriter.SHOW_DATAFRAME_INDEX)]
        config_file_path = props['path']
        path = os.path.join(config_file_path)

        class MockFile:
            def __init__(self):
                self.write_calls = []
                self.content = "existing content\n"
            
            def write(self, content):
                self.write_calls.append(content)
            
            def writelines(self, lines):
                self.write_calls.append(lines)
            
            def readlines(self):
                return [self.content]
            
            def read(self):
                return self.content
            
            def seek(self, pos):
                pass
            
            def truncate(self):
                pass
            
            def close(self):
                pass
            
            def __enter__(self):
                return self
            
            def __exit__(self, *args):
                pass

        mock_file = MockFile()
        
        def mock_open_func(file_path, mode):
            assert file_path == path
            assert mode == 'r+'
            return mock_file
        
        monkeypatch.setattr("builtins.open", mock_open_func)
        
        writer.add_header_footer(header, footer)
        assert header in mock_file.write_calls
        assert footer in mock_file.write_calls

    def test_excel_file_with_delimited_header(self):
        class MockDataFrame:
            def __init__(self):
                self.to_excel_calls = []
            
            def to_excel(self, path, index):
                self.to_excel_calls.append((path, index))

        mock_df = MockDataFrame()

        output_type = 'excel'
        props = {
            'path': '../output/positions.xlsx',
            'header': {'type': 'delimited_result_header',
                       'function': [{
                           'constant': "HMOCK"
                       }]}

        }

        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()
        assert mock_df.to_excel_calls == [(props['path'], InterfaceWriter.SHOW_DATAFRAME_INDEX)]

    def test_excel_file_without_delimited_header(self):
        class MockDataFrame:
            def __init__(self):
                self.to_excel_calls = []
            
            def to_excel(self, path, header, index):
                self.to_excel_calls.append((path, header, index))

        mock_df = MockDataFrame()

        output_type = 'excel'
        props = {
            'path': '../output/positions.xlsx',
            'header': {'type': 'custom',
                       'function': [{
                           'constant': "HMOCK"
                       }]}

        }

        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()
        assert mock_df.to_excel_calls == [(props['path'], False, InterfaceWriter.SHOW_DATAFRAME_INDEX)]

    def test_get_header_string(self):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, *args, **kwargs):
                self.to_csv_calls.append((args, kwargs))

        mock_df = MockDataFrame()

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
        writer = InterfaceWriter(mock_df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        actual_header = writer.get_header()
        assert actual_header == "HMOCK"

    def test_get_footer_string(self):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, *args, **kwargs):
                self.to_csv_calls.append((args, kwargs))

        mock_df = MockDataFrame()

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
        writer = InterfaceWriter(mock_df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        actual_footer = writer.get_footer()
        assert actual_footer == "TMOCK"

    def test_get_custom_value(self, monkeypatch):
        class MockDataFrame:
            def __init__(self):
                self.to_csv_calls = []
            
            def to_csv(self, *args, **kwargs):
                self.to_csv_calls.append((args, kwargs))

        mock_df = MockDataFrame()
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
        
        class MockGetCustomValue:
            def __init__(self):
                self.calls = []
            
            def __call__(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                return "mock_value"
        
        mock_get_custom_value = MockGetCustomValue()
        monkeypatch.setattr("ingen.writer.writer.get_custom_value", mock_get_custom_value)
        
        writer = InterfaceWriter(mock_df, output_type, props,
                                 {'query_params': None, 'run_date': datetime(2021, 12, 2, 0, 0)})
        writer.custom_function(props['header']['function'])
        writer.custom_function(props['footer']['function'])
        assert len(mock_get_custom_value.calls) > 0

    def test_json_writer_is_called(self, monkeypatch):
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
        
        class MockJSONWriter:
            def __init__(self, df, props):
                self.df = df
                self.props = props
                self.write_called = False
            
            def write(self):
                self.write_called = True

        mock_json_writer = MockJSONWriter(pd.DataFrame, config)
        
        def mock_json_writer_constructor(df, props, *args):
            return mock_json_writer
        
        monkeypatch.setattr("ingen.writer.writer.JSONWriter", mock_json_writer_constructor)

        writer = InterfaceWriter(pd.DataFrame, 'json_writer', config, {})
        writer.write()

        assert mock_json_writer.write_called

    def test_df_writer_is_called(self, monkeypatch):
        class MockDataFrame:
            pass

        mock_df = MockDataFrame()
        output_type = 'rawdatastore'

        props = {'id': 'DF1'}

        class MockDataFrameWriter:
            def __init__(self, df, props):
                self.df = df
                self.props = props
                self.write_called = False
            
            def write(self):
                self.write_called = True

        mock_df_writer = MockDataFrameWriter(mock_df, props)
        
        def mock_df_writer_constructor(df, props, *args):
            return mock_df_writer
        
        monkeypatch.setattr("ingen.writer.writer.DataFrameWriter", mock_df_writer_constructor)
        
        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.write()
        assert mock_df_writer.write_called

    def test_file_writer_multiple_paths(self, monkeypatch):
        class MockDataFrame:
            pass

        mock_df = MockDataFrame()
        output_type = 'json'
        props = {
            'path': ['../output/file1.json', '../output/file2.json'],
            'type': 'json'
        }

        class MockOldJSONWriter:
            def __init__(self, df, output_type, props):
                self.df = df
                self.output_type = output_type
                self.props = props
                self.write_called = False
            
            def write(self):
                self.write_called = True

        mock_writers = []
        
        def mock_json_writer_constructor(df, output_type, writer_props):
            writer = MockOldJSONWriter(df, output_type, writer_props)
            mock_writers.append(writer)
            return writer
        
        monkeypatch.setattr("ingen.writer.writer.OldJSONWriter", mock_json_writer_constructor)

        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()

        assert len(mock_writers) == 2
        assert all(w.write_called for w in mock_writers)

    def test_file_writer_single_path(self, monkeypatch):
        class MockDataFrame:
            pass

        mock_df = MockDataFrame()
        output_type = 'json'
        props = {
            'path': '../output/file1.json',  # path is now a string, not a list
            'type': 'json'
        }

        class MockOldJSONWriter:
            def __init__(self, df, output_type, props):
                self.df = df
                self.output_type = output_type
                self.props = props
                self.write_called = False
            
            def write(self):
                self.write_called = True

        mock_writers = []
        
        def mock_json_writer_constructor(df, output_type, writer_props):
            writer = MockOldJSONWriter(df, output_type, writer_props)
            mock_writers.append(writer)
            return writer
        
        monkeypatch.setattr("ingen.writer.writer.OldJSONWriter", mock_json_writer_constructor)

        writer = InterfaceWriter(mock_df, output_type, props, {})
        writer.file_writer()

        assert len(mock_writers) == 1
        assert mock_writers[0].write_called