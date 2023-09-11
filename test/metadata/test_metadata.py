#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os
import unittest
from datetime import date
from unittest.mock import patch

from ingen.data_source.data_source_type import DataSourceType
from ingen.data_source.json_source import JsonSource
from ingen.metadata.metadata import MetaData


class TestMetaData(unittest.TestCase):
    def setUp(self, arg=None):
        self.test_md_name = 'test interface'
        self.test_md_configurations = {
            'output': {
                'type': 'file',
                'props': {
                    'path': 'path/to/file/name_$date(%d%m%Y).csv',
                    'delimiter': ','
                }
            },
            'columns': [
                {
                    'id': 'sample-col',
                    'name': 'SAMPLE'
                }
            ],
            'sources': [
                {
                    'id': 'sample_source',
                    'type': DataSourceType.DB.value,
                    'db_token': 'DSREAD',
                    'query': 'select top 10 * from table_name'
                }
            ],
            'pre_processing': [
                {'type': 'merge', 'source': ['source1', 'source2'], 'key_column': 'id'}
            ],
            'validation_action': {
                'send_email': ['a_c@b.com']
            }
        }

        self.params_map = {'query_params': {'table_name': 'positions'}}
        self.query_params = {'table_name': 'positions'}
        # self.metadata = MetaData(self.test_md_name, self.test_md_configurations, self.params_map)
        self.test_md_configurations_splitted_file = {
            'output': {
                'type': 'splitted_file',
                'props': [
                    {
                        'col': 'col',
                        'value': 'val1',
                        'type': 'delimited_file',
                        'props':
                            {
                                'header':
                                    {
                                        'type': 'delimited_result_header'
                                    },
                                'delimiter': ',',
                                'path': 'path/to/file/name_val1$date(%d%m%Y).csv'
                            }
                    },
                    {
                        'col': 'col',
                        'value': 'val2',
                        'type': 'delimited_file',
                        'props':
                            {
                                'header':
                                    {
                                        'type': 'delimited_result_header'
                                    },
                                'delimiter': ',',
                                'path': 'path/to/file/name_val2$date(%d%m%Y).csv'
                            }
                    }
                ]
            },
            'columns': [
                {
                    'id': 'sample-col',
                    'name': 'SAMPLE'
                }
            ],
            'sources': [
                {
                    'id': 'sample_source',
                    'type': DataSourceType.DB.value,
                    'db_token': 'DSREAD',
                    'query': 'select top 10 * from <{table_name}>'
                }
            ],
            'pre_processing': [
                {'type': 'merge', 'source': ['source1', 'source2'], 'key_column': 'id'}
            ],
            'validation_action': {
                'send_email': ['a_c@b.com']
            }
        }

        self.query_params = {'table_name': 'positions'}
        self.params_map = {'query_params': self.query_params}
        if arg and arg.get('use_split_file_config'):
            self.metadata = MetaData(self.test_md_name, self.test_md_configurations_splitted_file, self.params_map)
        elif arg and arg.get('remove_output_props'):
            self.test_md_configurations.pop('output', None)
            self.metadata = MetaData(self.test_md_name, self.test_md_configurations, self.params_map)
        elif arg and arg.get('remove_columns'):
            self.test_md_configurations.pop('columns', None)
            self.metadata = MetaData(self.test_md_name, self.test_md_configurations, self.params_map)
        else:
            self.metadata = MetaData(self.test_md_name, self.test_md_configurations, self.params_map)

    def test_metadata_creates_sources(self):
        self.assertEqual(len(self.test_md_configurations['sources']), len(self.metadata.sources))

    def test_metadata_creates_params_map(self):
        self.assertEqual(self.params_map, self.metadata.params)

    def test_metadata_name(self):
        self.assertTrue(self.metadata.name, self.test_md_name)

    def test_metadata_columns(self):
        self.assertTrue(len(self.test_md_configurations['columns']), len(self.metadata.columns))

    def test_metadata_columns_not_given(self):
        self.setUp({'remove_columns': True})
        self.assertTrue(len(self.metadata.columns) == 0)

    def test_output_type(self):
        output = self.metadata.output
        self.assertEqual('file', output['type'])

    def test_output_type(self):
        self.setUp({'use_split_file_config': True})
        output = self.metadata.output
        self.assertEqual('splitted_file', output['type'])

    def test_output_props(self):
        output = self.metadata.output
        self.assertDictEqual(self.test_md_configurations['output']['props'], output['props'])

    def test_output_props_not_given(self):
        self.setUp({'remove_output_props': True})
        output = self.metadata.output
        self.assertDictEqual(dict(), output['props'])

    def test_output_props_for_splitted_file(self):
        self.setUp({'use_split_file_config': True})
        output = self.metadata.output
        self.assertListEqual(self.test_md_configurations_splitted_file['output']['props'], output['props'])

    def test_path_without_date(self):
        metadata_config = self.test_md_configurations
        metadata_config['output']['props']['path'] = '/some/path/name.csv'
        metadata = MetaData(self.test_md_name, metadata_config, self.params_map)

        output = metadata.output

        expected_path = f'/some/path/name.csv'
        self.assertEqual(expected_path, output.get('props').get('path'))

    def test_query_params(self):
        expected_query = 'select top 10 * from <positions>'
        source = self.metadata.sources[0]
        self.assertEqual(expected_query, source._query)

    def test_metadata_validation_action(self):
        self.assertTrue(len(self.test_md_configurations['validation_action']), len(self.metadata.validation_action))

    def test_pre_processing_columns(self):
        self.assertTrue(len(self.test_md_configurations['pre_processing']), len(self.metadata.pre_processes))

    def test_pre_processing_columns_returns_null_when_not_specified(self):
        config_without_pre_processing = self.test_md_configurations.copy()
        config_without_pre_processing.pop('pre_processing')

        temp_metadata = MetaData(self.test_md_name, config_without_pre_processing, self.params_map)
        self.assertIsNone(temp_metadata.pre_processes)

    @patch.dict(os.environ, {'FILE_SOURCE': 'test/file/path/'})
    def test_file_path_in_environment_variable(self):
        file_source = {
            'id': 'test_id',
            'type': 'file',
            'file_type': 'delimited_file',
            'file_path': '$$FILE_SOURCE'
        }
        metadata_config = self.test_md_configurations.copy()
        metadata_config['sources'].append(file_source)
        query_params = {'table_name': 'positions'}
        metadata = MetaData(self.test_md_name, metadata_config, query_params)

        expected_file_path = 'test/file/path/'
        self.assertEqual(expected_file_path, metadata.sources[1]._src['file_path'])

    @patch.dict(os.environ, {'FILE_SOURCE': 'test/file/path/name_$date(%d%m%Y).csv'})
    def test_file_path_in_environment_variable(self):
        file_source = {
            'id': 'test_id',
            'type': 'file',
            'file_type': 'delimited_file',
            'file_path': '$$FILE_SOURCE'
        }
        metadata_config = self.test_md_configurations.copy()
        metadata_config['sources'].append(file_source)
        query_params = {'table_name': 'positions'}
        params_map = {'query_params': {'table_name': 'positions'}}
        metadata = MetaData(self.test_md_name, metadata_config, params_map)
        today = date.today().strftime('%d%m%Y')

        expected_file_path = f'test/file/path/name_{today}.csv'
        self.assertEqual(expected_file_path, metadata.sources[1]._src['file_path'])

    def test_sources_with_dynamic_data(self):
        json_source = {
            'id': 'json_payload',
            'type': 'json'
        }
        dynamic_data = """ {
            "json_payload": {
                    "account" : "ABC123",
                    "type" : "New Enrollment",
                    "status" : "New",
                    "platform" : "SERVER"
                }
        }"""
        metadata_config = self.test_md_configurations.copy()
        metadata_config['sources'].append(json_source)
        metadata = MetaData(self.test_md_name, metadata_config, self.params_map, dynamic_data)

        self.assertIsInstance(metadata.sources[1], JsonSource)
        self.assertEqual('json_payload', metadata.sources[1]._id)


if __name__ == '__main__':
    unittest.main()
