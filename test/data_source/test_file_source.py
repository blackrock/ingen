#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from unittest.mock import Mock

import pandas as pd

from ingen.data_source.file_source import FileSource


class TestFileSource:

    def setup_method(self):
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

    def test_source_fetch(self, monkeypatch):
        mock_reader_factory = Mock()
        fileReader = Mock()
        fileReader.read.return_value = pd.DataFrame()
        mock_reader_factory.get_reader.return_value = fileReader
        monkeypatch.setattr('ingen.data_source.file_source.ReaderFactory', mock_reader_factory)
        
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
        assert config.get('src_data_checks') == expected
