import unittest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.data_source.file_source import FileSource


class TestFileSource(unittest.TestCase):

    def setUp(self):
        self._src = {
            'id': 'open_lot_file',
            'type': 'file',
            'file_type': 'delimited_file',
            'delimiter': '|',
            'file_path': 'test',
            'skip_header_size': 1,
            'skip_trailer_size': 1,
            'columns': ['col1', 'col2']

        }
        self.params_map = {'query_params': {'table_name': 'positions'}, 'infile': {}}
        self.source = FileSource(self._src, self.params_map)

    @patch('src.data_source.file_source.ReaderFactory')
    def test_source_fetch(self, mock_reader_factory):
        fileReader = Mock()
        fileReader.read.return_value = pd.DataFrame()
        mock_reader_factory.get_reader.return_value = fileReader
        result = self.source.fetch()
        pd.testing.assert_frame_equal(result, pd.DataFrame())

    def test_fetch_validation(self):
        config = {
            'src_data_checks': [
                {'src_col_name': 'cusip',
                 'validations': [
                     {'type': 'expect_column_values_to_be_of_type', 'severity': 'critical', 'args': ['str']},
                 ]
                 }
            ]
        }
        params_map = {'query_params': {'table_name': 'positions'}, 'infile': {}}

        source = FileSource(config, params_map)
        expected = source.fetch_validations()
        self.assertEqual(config.get('src_data_checks'), expected)


if __name__ == '__main__':
    unittest.main()
