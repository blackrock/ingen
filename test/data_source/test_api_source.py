import unittest
from unittest.mock import patch, Mock

from ingen.data_source.api_source import APISource
from ingen.utils.app_http.HTTPRequest import HTTPRequest
from ingen.utils.app_http.success_criterias import status_criteria, DEFAULT_STATUS_CRITERIA_OPTIONS
from ingen.utils.url_constructor import UrlConstructor


class TestAPISource(unittest.TestCase):

    def setUp(self):
        self._src = {
            'id': 'test data source',
            'url': 'abc',
            'batch': {
                'size': 50,
                'id': 'portfolioIds'
            },
            'url_params': [{
                'id': 'portfolioIds',
                'type': 'const',
                'value': 'APPROVED',
            }],
            'method': 'GET',
            'data_key': [],
            'data_node': ['holdings'],
            'meta': ['meta-field'],
            'auth':
                {'type': 'HTPBasicAuth',
                 'username': 'TEST_USER',
                 'pwd': 'TEST_PWD'
                 }
        }
        self.default_reader_params = {
            'response_to_list': None,
            'convertor_method': None,
            'retries': 2,
            'interval': 1,
            'interval_increment': 2,
            'success_criteria': status_criteria,
            'criteria_options': DEFAULT_STATUS_CRITERIA_OPTIONS,
            'tasks_len': 1,
            'queue_size': 1,
            'ssl': True,
            'ignore_failure': True
        }
        self.source = APISource(self._src)

    @patch('ingen.data_source.api_source.APIReader')
    def test_source_fetch(self, mock_api_reader):
        url_constructor = UrlConstructor(self._src.get('url'), self._src.get('url_params'), self._src.get('batch'))
        urls = url_constructor.get_urls()
        requests = [HTTPRequest(url=url, method=self._src.get('method'), auth=self._src.get('auth')) for url in urls]
        mock_reader_obj = Mock()
        mock_api_reader.return_value = mock_reader_obj

        self.source.fetch()

        mock_api_reader.assert_called_with(requests, self.default_reader_params)
        mock_reader_obj.execute.assert_called_with(self._src['data_node'], self._src['data_key'], self._src['meta'])

    def test_headers_are_parsed_correctly(self):
        mock_interpolator = Mock()
        mock_interpolator.interpolate.return_value = "mock_value"
        source_config = self._src.copy()
        source_config['headers'] = {
            'custom_header': '$token(token_name)'
        }
        source_with_headers = APISource(source_config, interpolator=mock_interpolator)
        header_value = source_with_headers._headers.get('custom_header')
        expected_header_value = "mock_value"
        self.assertEqual(expected_header_value, header_value)

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

        source = APISource(config)
        expected = source.fetch_validations()
        self.assertEqual(config.get('src_data_checks'), expected)


if __name__ == '__main__':
    unittest.main()
