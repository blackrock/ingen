import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from ingen.data_source.file_source import FileSource
from ingen.reader.file_reader import ReaderFactory


class TestFileReader(unittest.TestCase):
    @patch('ingen.data_source.file_source')
    def setUp(self, mock):
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

    @patch('ingen.reader.file_reader.pd')
    def test_read_all_columns(self, mock_pandas):
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

        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        mock_pandas.read_csv.assert_called_with(
            source['file_path'],
            sep=source['delimiter'],
            index_col=False,
            skiprows=0,
            skipfooter=0,
            names=source['columns'],
            dtype=None
        )

    @patch('ingen.reader.file_reader.pd')
    def test_column_dtype(self, mock_pandas):
        source = self._src
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        mock_pandas.read_csv.assert_called_with(
            source['file_path'],
            sep=source['delimiter'],
            index_col=False,
            skiprows=1,
            skipfooter=1,
            names=source['columns'],
            dtype=source['dtype']
        )

    @patch('ingen.reader.file_reader.pd')
    def test_dtype_excel(self, mock_pandas):
        source = self.excel_src
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        mock_pandas.read_excel.assert_called_with(
            source['file_path'],
            sheet_name=0,
            index_col=False,
            skiprows=0,
            skipfooter=0,
            names=source['columns'],
            dtype=source['dtype'],
            engine=None
        )

    @patch('ingen.reader.file_reader.pd')
    def test_xlsx_reader_engine(self, mock_pandas):
        source = self.excel_src
        source['file_path'] = 'test.xlsx'
        reader = ReaderFactory.get_reader(source)
        reader.read(source)

        mock_pandas.read_excel.assert_called_with(
            source['file_path'],
            sheet_name=0,
            index_col=False,
            skiprows=0,
            skipfooter=0,
            names=source['columns'],
            dtype=source['dtype'],
            engine='openpyxl'
        )

    @patch('ingen.reader.file_reader.logging')
    def test_exception_incorrect_dtype(self, mock_logging):
        source = self._src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }
        reader = ReaderFactory.get_reader(source)
        with tempfile.NamedTemporaryFile() as file_object:
            source['file_path'] = file_object.name
            with self.assertRaises(TypeError):
                reader.read(source)

            error_msg = "Invalid data type provided in column_dtype mapping"
            mock_logging.error.assert_called_with(error_msg)

    def test_file_not_found(self):
        source = self._src
        reader = ReaderFactory.get_reader(source)
        with self.assertRaises(FileNotFoundError):
            reader.read(source)

    def test_file_not_found_when_flag_true(self):
        source = self._src
        source['return_empty_if_not_exist'] = True

        reader = ReaderFactory.get_reader(source)
        data = reader.read(source)
        self.assertTrue(data.empty)

    @patch('ingen.reader.file_reader.logging')
    def test_exception_incorrect_dtype_for_excel(self, mock_logging):
        source = self.excel_src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }

        with tempfile.NamedTemporaryFile(suffix=".xlsx") as file_object:
            df = pd.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})
            df.to_excel(file_object.name)
            source['file_path'] = file_object.name
            reader = ReaderFactory.get_reader(source)
            with self.assertRaises(TypeError):
                reader.read(source)
            error_msg = "Invalid data type provided in column_dtype mapping"
            mock_logging.error.assert_called_with(error_msg)

    @patch('ingen.reader.file_reader.pd')
    def test_fixed_width_reader(self, mock_pandas):
        source = self.fixedwidth_src
        reader = ReaderFactory.get_reader(source)
        reader.read(source)
        mock_pandas.read_fwf.assert_called_with(source['file_path'], index_col=False,
                                                colspecs=source['col_specification'],
                                                dtype=source['dtype'],
                                                skiprows=1,
                                                skipfooter=1,
                                                names=source['columns']
                                                )

    @patch('ingen.reader.file_reader.pd')
    def test_fixed_width_reader_with_widthindices(self, mock_pandas):
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

        reader = ReaderFactory.get_reader(source)
        reader.read(source)
        mock_pandas.read_fwf.assert_called_with(source['file_path'], index_col=False,
                                                colspecs=source['col_specification'],
                                                dtype=source['dtype'],
                                                skiprows=1,
                                                skipfooter=1,
                                                names=source['columns']
                                                )

    @patch('ingen.reader.file_reader.logging')
    def test_exception_incorrect_dtype_for_fixedwidth(self, mock_logging):
        source = self.fixedwidth_src
        source['dtype'] = {
            'col1': 'incorrect_dtype'
        }
        source['col_specification'] = [(0, 20), (21, 30)]
        reader = ReaderFactory.get_reader(source)
        with tempfile.NamedTemporaryFile() as file_object:
            source['file_path'] = file_object.name
            with self.assertRaises(TypeError):
                reader.read(source)

            error_msg = "Invalid data type provided in column_dtype mapping"
            mock_logging.error.assert_called_with(error_msg)


if __name__ == '__main__':
    unittest.main()
