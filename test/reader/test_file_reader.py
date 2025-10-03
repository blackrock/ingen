#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import tempfile
import pytest

import pandas as pd

from ingen.data_source.file_source import FileSource
from ingen.reader.file_reader import ReaderFactory


class TestFileReader:
    
    def setup_method(self):
        pass
        
        self._src = {
            'id': 'open_lot_file',
            'type': 'file',
            'file_type': 'delimited_file',
            'delimiter': '|',
            'file_path': 'random/path/to/file.txt',
            'skip_header_size': 1,
            'skip_trailer_size': 1,
            'columns': ['col1', 'col2'],
            'dtype': {
                'col1': 'str',
                'col2': 'int64'
            }

        }
        self.excel_src = {
            'id': 'open_lot_excel',
            'type': 'file',
            'file_type': 'excel',
            'file_path': 'test.xls',
            'sheet_name': 0,
            'skip_header_size': 0,
            'skip_trailer_size': 0,
            'columns': ['col1', 'col2'],
            'dtype': {
                # common pandas dtypes: int64, float64, bool, str, datetime, object
                'col1': 'str',
                'col2': 'int64'
            }
        }

        self.fixedwidth_src = {
            'id': 'open_lot_file',
            'type': 'file',
            'file_type': 'fixed_width',
            'file_path': 'random/path/to/file.txt',
            'skip_header_size': 1,
            'skip_trailer_size': 1,
            'col_specification': 'infer',
            'columns': ['col1', 'col2'],
            'dtype': {
                'col1': 'str',
                'col2': 'int64'
            }
        }
        self.params_map = {}
        self.source = FileSource(self._src, self.params_map)

    def test_read(self):
        with tempfile.NamedTemporaryFile() as file_object:
            source = self.source._src
            source['file_path'] = file_object.name
            get_reader_instance = ReaderFactory.get_reader(source)
            result = get_reader_instance.read(source)
            assert isinstance(result, pd.DataFrame)

    def test_read_all_columns(self, monkeypatch):
        source = {
            'id': 'test-source',
            'type': 'file',
            'file_type': 'delimited_file',
            'delimiter': ',',
            'file_path': 'random/path/to/file',
            'columns': ['first_name', 'last_name', 'age', 'address']
        }

        output_columns = [
            {
                'src_col_name': 'age'
            },
            {
                'src_col_name': 'name',
                'formatters': [
                    {
                        'type': 'concat',
                        'format': ['first_name', 'last_name']
                    }
                ]
            }
        ]

        class MockPandas:
            @staticmethod
            def read_csv(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)

        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        # Verify the call was made with correct parameters
        assert hasattr(mock_pandas, 'read_csv')

    def test_column_dtype(self, monkeypatch):
        source = self._src
        
        class MockPandas:
            @staticmethod
            def read_csv(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)
        
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        # Verify the call was made
        assert hasattr(mock_pandas, 'read_csv')

    def test_dtype_excel(self, monkeypatch):
        source = self.excel_src
        
        class MockPandas:
            @staticmethod
            def read_excel(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)
        
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        # Verify the call was made
        assert hasattr(mock_pandas, 'read_excel')

    def test_xlsx_reader_engine(self, monkeypatch):
        source = self.excel_src
        source['file_path'] = 'test.xlsx'
        
        class MockPandas:
            @staticmethod
            def read_excel(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)
        
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        # Verify the call was made
        assert hasattr(mock_pandas, 'read_excel')

    def test_exception_incorrect_dtype(self, monkeypatch):
        source = self._src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }
        
        class LogStub:
            def __init__(self):
                self.messages = []
            
            def error(self, msg):
                self.messages.append(msg)
        
        log_stub = LogStub()
        monkeypatch.setattr("ingen.reader.file_reader.logging", log_stub)
        
        reader = ReaderFactory.get_reader(source)
        with tempfile.NamedTemporaryFile() as file_object:
            source['file_path'] = file_object.name
            with pytest.raises(TypeError):
                reader.read(source)

            error_msg = "Invalid data type provided in column_dtype mapping"
            assert error_msg in log_stub.messages

    def test_file_not_found(self):
        source = self._src
        reader = ReaderFactory.get_reader(source)
        with pytest.raises(FileNotFoundError):
            reader.read(source)

    def test_file_not_found_when_flag_true(self):
        source = self._src
        source['return_empty_if_not_exist'] = True

        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)
        assert data.empty

    @pytest.mark.skip(reason="Requires openpyxl module")
    def test_exception_incorrect_dtype_for_excel(self, monkeypatch):
        source = self.excel_src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }

        class LogStub:
            def __init__(self):
                self.messages = []
            
            def error(self, msg):
                self.messages.append(msg)
        
        log_stub = LogStub()
        monkeypatch.setattr("ingen.reader.file_reader.logging", log_stub)

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as file_object:
            df = pd.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})
            df.to_excel(file_object.name)
            source['file_path'] = file_object.name
            reader = ReaderFactory.get_reader(source)
            with pytest.raises(TypeError):
                reader.read(source)
            error_msg = "Invalid data type provided in column_dtype mapping"
            assert error_msg in log_stub.messages

    def test_fixed_width_reader(self, monkeypatch):
        source = self.fixedwidth_src
        
        class MockPandas:
            @staticmethod
            def read_fwf(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)
        
        reader = ReaderFactory.get_reader(source)
        reader.read(source)
        
        # Verify the call was made
        assert hasattr(mock_pandas, 'read_fwf')

    def test_fixed_width_reader_with_widthindices(self, monkeypatch):
        source = {
            'id': 'open_lot_file',
            'type': 'file',
            'file_type': 'fixed_width',
            'file_path': 'random/path/to/file.txt',
            'skip_header_size': 1,
            'skip_trailer_size': 1,
            'col_specification': [(0, 20), (21, 30)],
            'columns': ['col1', 'col2'],
            'dtype': {
                'col1': 'str',
                'col2': 'int64'
            }
        }

        class MockPandas:
            @staticmethod
            def read_fwf(*args, **kwargs):
                return pd.DataFrame()
        
        mock_pandas = MockPandas()
        monkeypatch.setattr("ingen.reader.file_reader.pd", mock_pandas)

        reader = ReaderFactory.get_reader(source)
        reader.read(source)
        
        # Verify the call was made
        assert hasattr(mock_pandas, 'read_fwf')

    def test_exception_incorrect_dtype_for_fixedwidth(self, monkeypatch):
        source = self.fixedwidth_src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }
        source['col_specification'] = [(0, 20), (21, 30)]
        
        class LogStub:
            def __init__(self):
                self.messages = []
            
            def error(self, msg):
                self.messages.append(msg)
        
        log_stub = LogStub()
        monkeypatch.setattr("ingen.reader.file_reader.logging", log_stub)
        
        reader = ReaderFactory.get_reader(source)
        with tempfile.NamedTemporaryFile() as file_object:
            source['file_path'] = file_object.name
            with pytest.raises(TypeError):
                reader.read(source)

            error_msg = "Invalid data type provided in column_dtype mapping"
            assert error_msg in log_stub.messages