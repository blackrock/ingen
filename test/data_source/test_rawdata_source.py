import unittest
from unittest.mock import patch, Mock

from ingen.data_source.dataframe_store import store
from ingen.data_source.rawdata_source import RawDataSource


class TestRawDataStoreSource(unittest.TestCase):

    def setUp(self):
        self._src = {

            'id': 'contact'

        }
        self.source = RawDataSource(self._src)

    @patch('ingen.data_source.rawdata_source.RawDataReader')
    def test_source_fetch(self, mock_reader_class):
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        result = self.source.fetch()
        mock_reader.read.assert_called_with(self._src.get('id'), store)

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

        source = RawDataSource(config)
        expected = source.fetch_validations()
        self.assertEqual(config.get('src_data_checks'), expected)


if __name__ == '__main__':
    unittest.main()
