import logging
import unittest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.utils.app_http.HTTPRequest import HTTPRequest
from ingen.utils.app_http.success_criterias import get_criteria_by_name
from ingen.writer.json_writer.destinations.api_destination import ApiDestination


class TestApiDestination(unittest.TestCase):
    def setUp(self) -> None:
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

    @patch('ingen.writer.json_writer.destinations.api_destination.DataFrameWriter')
    @patch('ingen.writer.json_writer.destinations.api_destination.APIReader')
    def test_api_destination_calls_api_reader(self, mock_api_reader_class, mock_df_writer_class):
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

        mock_reader = Mock()
        mock_reader.execute.return_value = fake_response_data
        mock_api_reader_class.return_value = mock_reader

        mock_writer = Mock()
        mock_df_writer_class.return_value = mock_writer

        destination = ApiDestination()
        destination.handle(json_strings, destination_props)

        mock_api_reader_class.assert_called_with(expected_requests, expected_reader_props)
        mock_reader.execute.assert_called_with(self.api_response_props.get('data_node'),
                                               self.api_response_props.get('data_key'))

        writer_props = {
            'id': self.api_response_props.get('dataframe_id')
        }
        mock_df_writer_class.assert_called_with(fake_response_data, writer_props)
        mock_writer.write.assert_called()

    def test_raises_value_error_with_invalid_json(self):
        # valid json strings are enclosed in double quotes, not single quote
        invalid_json_strings = ["{'name': 'sample'}"]

        # empty for this test case
        destination_props = {
            'api_request_props': self.api_request_props,
            'api_response_props': self.api_response_props
        }

        with self.assertRaisesRegex(ValueError, "Invalid JSON strings"):
            destination = ApiDestination()
            destination.handle(invalid_json_strings, destination_props)

    @patch('ingen.writer.json_writer.destinations.api_destination.APIReader')
    def test_logs_when_response_data_is_empty(self, mock_api_reader_class):
        json_strings = ['{"sample_json": 1}']

        destination_props = {
            'api_request_props': self.api_request_props,
            'api_response_props': self.api_response_props
        }

        # empty dataframe
        fake_response_data = pd.DataFrame()

        mock_reader = Mock()
        mock_reader.execute.return_value = fake_response_data
        mock_api_reader_class.return_value = mock_reader

        log = logging.getLogger()
        with patch.object(log, 'warning') as mock_warning:
            destination = ApiDestination()
            destination.handle(json_strings, destination_props)
            mock_warning.assert_called_with("Received empty response from API call. Writing empty dataframe to "
                                            "dataframe store.")


if __name__ == '__main__':
    unittest.main()
