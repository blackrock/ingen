#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os
import unittest
from unittest.mock import patch

from ingen.data_source.file_source import FileSource
from ingen.data_source.snowflake_source import SnowflakeSource
from ingen.data_source.source_factory import SourceFactory


class TestSourceFactory(unittest.TestCase):

    @patch.dict(os.environ, {'FILE_SOURCE': 'test/file/path/name_$date(%d%m%Y).csv'})
    def test_parse_source_for_file(self):
        environment_var = 'FILE_SOURCE'
        file_source = {
            'id': 'test_id',
            'type': 'file',
            'file_type': 'delimited_file',
            'file_path': f'$${environment_var}'
        }
        params_map = {'query_params': {'table_name': 'positions'}}
        sf = SourceFactory()
        file = sf.parse_source(file_source, params_map)
        self.assertIsInstance(file, FileSource)
        self.assertEqual(file._src, file_source)

    @patch('ingen.data_source.snowflake_source.properties')
    def test_parse_source_for_snowflake(self, mock_properties):
        mock_properties.get_property.side_effect = lambda key, default=None: {
            'datasource.snowflake.account': 'acc',
            'datasource.snowflake.user': 'u',
            'datasource.snowflake.password': 'p',
        }.get(key, default)
        source = {'id': 'sf', 'type': 'snowflake', 'query': 'select * from {table_name}'}
        params_map = {'query_params': {'table_name': 'positions'}}
        snowflake = SourceFactory().parse_source(source, params_map)
        self.assertIsInstance(snowflake, SnowflakeSource)
        self.assertEqual('select * from positions', snowflake._query)


if __name__ == "__main__":
    unittest.main()
