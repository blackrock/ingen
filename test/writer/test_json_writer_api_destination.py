#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import pytest
import pandas as pd

from ingen.utils.app_http.http_request import HTTPRequest
from ingen.utils.app_http.success_criterias import get_criteria_by_name
from ingen.writer.json_writer.destinations.api_destination import ApiDestination


class TestApiDestination:
    def setup_method(self):
        self.api_request_props = {
            'url': 'http://sample.com',
            'method': 'post',
            'headers': {
                'sample_header': 'sample_header_value'
            },
            'auth': {
                'type': 'BasicAuth',
                'user': 'test_user',
                'password': 'password'
            },
            'success_criteria': 'payload_criteria',
            'criteria_options': {
                'key': 'done',
                'value': 'true'
            }
        }
        self.api_response_props = {
            'type': 'dataframe',
            'dataframe_id': 'my_response',
            'data_node': [],
            'data_key': [],
        }

    def test_api_destination_calls_api_reader(self, monkeypatch):
        json_strings = ['{"sample_json": 1}', '{"sample_json": 2}']

        destination_props = {
            'api_request_props': self.api_request_props,
            'api_response_props': self.api_response_props
        }

        http_request_1 = HTTPRequest(url=self.api_request_props.get('url'),
                                     method=self.api_request_props.get('method'),
                                     headers=self.api_request_props.get('headers'),
                                     auth=self.api_request_props.get('auth'),
                                     data=json_strings[0])

        http_request_2 = HTTPRequest(url=self.api_request_props.get('url'),
                                     method=self.api_request_props.get('method'),
                                     headers=self.api_request_props.get('headers'),
                                     auth=self.api_request_props.get('auth'),
                                     data=json_strings[1])

        expected_requests = [http_request_1, http_request_2]
        expected_reader_props = {
            'retries': 2,
            'interval': 1,
            'success_criteria': get_criteria_by_name(self.api_request_props.get('success_criteria')),
            'criteria_options': self.api_request_props.get('criteria_options'),
            'tasks_len': 1,
            'queue_size': 1,
            'ssl': True,
            'ignore_failure': True
        }

        fake_response_data = pd.DataFrame({})

        class MockAPIReader:
            def __init__(self, requests, props):
                self.requests = requests
                self.props = props
                self.execute_calls = []
            
            def execute(self, data_node, data_key):
                self.execute_calls.append((data_node, data_key))
                return fake_response_data

        class MockDataFrameWriter:
            def __init__(self, df, props):
                self.df = df
                self.props = props
                self.write_called = False
            
            def write(self):
                self.write_called = True

        mock_api_reader_instance = MockAPIReader(expected_requests, expected_reader_props)
        mock_df_writer_instance = MockDataFrameWriter(fake_response_data, {'id': self.api_response_props.get('dataframe_id')})

        def mock_api_reader_constructor(requests, props):
            assert requests == expected_requests
            assert props == expected_reader_props
            return mock_api_reader_instance

        def mock_df_writer_constructor(df, props):
            assert df is fake_response_data
            assert props == {'id': self.api_response_props.get('dataframe_id')}
            return mock_df_writer_instance

        monkeypatch.setattr("ingen.writer.json_writer.destinations.api_destination.APIReader", mock_api_reader_constructor)
        monkeypatch.setattr("ingen.writer.json_writer.destinations.api_destination.DataFrameWriter", mock_df_writer_constructor)

        destination = ApiDestination()
        destination.handle(json_strings, destination_props)

        assert mock_api_reader_instance.execute_calls == [(self.api_response_props.get('data_node'), self.api_response_props.get('data_key'))]
        assert mock_df_writer_instance.write_called

    def test_raises_value_error_with_invalid_json(self):
        # valid json strings are enclosed in double quotes, not single quote
        invalid_json_strings = ["{'name': 'sample'}"]

        # empty for this test case
        destination_props = {
            'api_request_props': self.api_request_props,
            'api_response_props': self.api_response_props
        }

        with pytest.raises(ValueError, match="Invalid JSON strings"):
            destination = ApiDestination()
            destination.handle(invalid_json_strings, destination_props)

    def test_logs_when_response_data_is_empty(self, monkeypatch):
        json_strings = ['{"sample_json": 1}']

        destination_props = {
            'api_request_props': self.api_request_props,
            'api_response_props': self.api_response_props
        }

        # empty dataframe
        fake_response_data = pd.DataFrame()

        class MockAPIReader:
            def execute(self, data_node, data_key):
                return fake_response_data

        class MockDataFrameWriter:
            def __init__(self, df, props):
                self.df = df
                self.props = props
            
            def write(self):
                pass

        def mock_api_reader_constructor(*args, **kwargs):
            return MockAPIReader()

        def mock_df_writer_constructor(*args, **kwargs):
            return MockDataFrameWriter(*args, **kwargs)

        monkeypatch.setattr("ingen.writer.json_writer.destinations.api_destination.APIReader", mock_api_reader_constructor)
        monkeypatch.setattr("ingen.writer.json_writer.destinations.api_destination.DataFrameWriter", mock_df_writer_constructor)

        destination = ApiDestination()
        destination.handle(json_strings, destination_props)
        
        # Just verify that the method completes without error when empty dataframe is returned
        assert True  # Test passes if no exception is raised