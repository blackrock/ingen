#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from unittest.mock import Mock

from ingen.data_source.dataframe_store import store
from ingen.data_source.rawdata_source import RawDataSource


class TestRawDataStoreSource:

    def setup_method(self):
        self._src = {

            'id': 'contact'

        }
        self.source = RawDataSource(self._src)

    def test_source_fetch(self, monkeypatch):
        mock_reader_class = Mock()
        mock_reader = Mock()
        mock_reader_class.return_value = mock_reader
        monkeypatch.setattr('ingen.data_source.rawdata_source.RawDataReader', mock_reader_class)
        
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
        assert config.get('src_data_checks') == expected
