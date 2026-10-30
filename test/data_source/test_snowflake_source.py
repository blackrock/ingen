#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch

from pandas import DataFrame

from ingen.data_source.data_source_type import DataSourceType
from ingen.data_source.snowflake_source import SnowflakeSource


def mock_properties(**props):
    values = {f'datasource.snowflake.{key}': value for key, value in props.items()}
    return lambda key, default=None: values.get(key, default)


@patch('ingen.data_source.snowflake_source.properties')
class SnowflakeSourceTest(unittest.TestCase):

    def setUp(self):
        self.input_source = {
            'id': 'sample_source',
            'type': DataSourceType.Snowflake.value,
            'warehouse': 'SAMPLE_WH',
            'database': 'SAMPLE_DB',
            'schema': 'PUBLIC',
            'role': 'READER',
            'query': 'select * from {table_name}'
        }
        self.params_map = {'query_params': {'table_name': 'SAMPLE_TABLE'}}

    def test_query_params_substituted(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        source = SnowflakeSource(self.input_source, self.params_map)
        self.assertEqual('select * from SAMPLE_TABLE', source._query)

    def test_password_auth(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        source = SnowflakeSource(self.input_source, self.params_map)
        self.assertEqual({
            'account': 'acc', 'authenticator': 'snowflake', 'user': 'u', 'password': 'p',
            'warehouse': 'SAMPLE_WH', 'database': 'SAMPLE_DB', 'schema': 'PUBLIC', 'role': 'READER',
        }, source._connection_params)

    def test_key_pair_auth_inferred_and_preferred(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p',
                                                         private_key_path='/keys/rsa_key.p8',
                                                         private_key_passphrase='secret')
        params = SnowflakeSource(self.input_source, self.params_map)._connection_params
        self.assertEqual('snowflake_jwt', params['authenticator'])
        self.assertEqual('/keys/rsa_key.p8', params['private_key_file'])
        self.assertEqual('secret', params['private_key_file_pwd'])
        self.assertNotIn('password', params)

    def test_key_pair_auth_without_passphrase(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', private_key_path='/keys/rsa_key.p8')
        params = SnowflakeSource(self.input_source, self.params_map)._connection_params
        self.assertNotIn('private_key_file_pwd', params)

    def test_oauth_auth_inferred(self, props):
        props.get_property.side_effect = mock_properties(account='acc', token='oauth_token')
        params = SnowflakeSource(self.input_source, self.params_map)._connection_params
        self.assertEqual('oauth', params['authenticator'])
        self.assertEqual('oauth_token', params['token'])
        self.assertNotIn('user', params)

    def test_external_browser_requires_explicit_authenticator(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u')
        with self.assertRaisesRegex(ValueError, 'No Snowflake credentials found'):
            SnowflakeSource(self.input_source, self.params_map)

        self.input_source['authenticator'] = 'ExternalBrowser'
        with self.assertLogs(level='WARNING') as logs:
            params = SnowflakeSource(self.input_source, self.params_map)._connection_params
        self.assertEqual('externalbrowser', params['authenticator'])
        self.assertIn('local use only', logs.output[0])

    def test_explicit_authenticator_overrides_inference(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p',
                                                         private_key_path='/keys/rsa_key.p8')
        self.input_source['authenticator'] = 'snowflake'
        params = SnowflakeSource(self.input_source, self.params_map)._connection_params
        self.assertEqual('snowflake', params['authenticator'])
        self.assertNotIn('private_key_file', params)

    def test_unsupported_authenticator(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        self.input_source['authenticator'] = 'okta'
        with self.assertRaisesRegex(ValueError, "Unsupported Snowflake authenticator 'okta'"):
            SnowflakeSource(self.input_source, self.params_map)

    def test_temp_table_params_not_supported(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        self.input_source['temp_table_params'] = [{'type': 'file', 'temp_table_name': 't'}]
        with self.assertRaisesRegex(ValueError, 'temp_table_params is not supported'):
            SnowflakeSource(self.input_source, self.params_map)

    def test_missing_account(self, props):
        props.get_property.side_effect = mock_properties(user='u', password='p')
        with self.assertRaisesRegex(ValueError, 'datasource.snowflake.account'):
            SnowflakeSource(self.input_source, self.params_map)

    def test_missing_credentials_for_authenticator(self, props):
        props.get_property.side_effect = mock_properties(account='acc', password='p')
        with self.assertRaisesRegex(ValueError, 'datasource.snowflake.user'):
            SnowflakeSource(self.input_source, self.params_map)

    def test_session_keys_optional(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        source = {'id': 'sample_source', 'type': 'snowflake', 'query': 'select 1'}
        params = SnowflakeSource(source)._connection_params
        for key in ('warehouse', 'database', 'schema', 'role'):
            self.assertNotIn(key, params)

    @patch('ingen.data_source.snowflake_source.SnowflakeReader')
    @patch('snowflake.connector.connect')
    def test_fetch(self, mock_connect, mock_reader, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        mock_reader.return_value.execute.return_value = DataFrame()
        source = SnowflakeSource(self.input_source, self.params_map)

        data = source.fetch()

        assert data.size == 0
        mock_connect.assert_called_once_with(**source._connection_params)
        mock_reader.assert_called_once_with(mock_connect.return_value)
        mock_reader.return_value.execute.assert_called_once_with('select * from SAMPLE_TABLE')

    def test_fetch_validations(self, props):
        props.get_property.side_effect = mock_properties(account='acc', user='u', password='p')
        assert len(SnowflakeSource(self.input_source, self.params_map).fetch_validations()) == 0


if __name__ == '__main__':
    unittest.main()
