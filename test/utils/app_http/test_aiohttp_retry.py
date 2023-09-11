#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import unittest
from unittest.mock import MagicMock, Mock

from ingen.utils.app_http.aiohttp_retry import http_retry_request


class MockSession(MagicMock):
    """
    Helper class to create Mock for Async Context Manager
    """

    async def __aenter__(self, *args, **kwargs):
        return self.__enter__(*args, **kwargs)

    async def __aexit__(self, *args, **kwargs):
        return self.__exit__(*args, **kwargs)


def passing_success_criteria(response, option):
    """
    Mock success criteria that always returns True
    """
    return True


def failing_success_criteria(response, option):
    """
        Mock success criteria that always returns False
    """
    return False


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self) -> None:
        self.loop.close()

    def test_http_get_retry(self):
        mock_session = MockSession()
        mock_response = Mock()
        future_json = asyncio.Future()
        future_json.set_result({'data': 123})
        mock_response.json.return_value = future_json
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/json'}

        mock_session.get.return_value.__enter__.return_value = mock_response
        http_response = self.loop.run_until_complete(http_retry_request(mock_session,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=2,
                                                                        interval=1,
                                                                        success_criteria=passing_success_criteria))

        self.assertEqual(http_response.status, 200)
        self.assertDictEqual(http_response.headers, {'Content-Type': 'application/json'})
        self.assertDictEqual(http_response.data, {'data': 123})
        self.assertEqual(mock_session.get.call_count, 1)

    def test_http_retry_request_sends_none_when_success_criteria_fails(self):
        mock_session = MockSession()
        mock_response = Mock()
        future_json = asyncio.Future()
        future_json.set_result({'done': False})
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = future_json
        mock_session.get.return_value.__enter__.return_value = mock_response
        http_response = self.loop.run_until_complete(http_retry_request(mock_session,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=2,
                                                                        interval=1,
                                                                        success_criteria=failing_success_criteria))

        self.assertIsNone(http_response)
        # one call + 2 retries
        self.assertEqual(mock_session.get.call_count, 3)

    def test_http_retry_when_connection_exception_occurs(self):
        mock_session = MockSession()
        mock_response = Mock()
        future_json = asyncio.Future()
        future_json.set_exception(Exception)
        mock_response.json.return_value = future_json

        mock_session.get.return_value.__enter__.return_value = mock_response

        with self.assertRaises(ConnectionError):
            http_response = self.loop.run_until_complete(http_retry_request(mock_session,
                                                                            'get',
                                                                            'test.com',
                                                                            retries=2,
                                                                            interval=1))

        self.assertEqual(mock_session.get.call_count, 1)

    def test_http_retry_when_retry_is_zero(self):
        mock_session = MockSession()
        mock_response = Mock()
        future_json = asyncio.Future()
        future_json.set_result({'done': False})
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = future_json
        mock_session.get.return_value.__enter__.return_value = mock_response
        http_response = self.loop.run_until_complete(http_retry_request(mock_session,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=0,
                                                                        success_criteria=failing_success_criteria))

        self.assertIsNone(http_response)
        # one call, no retries
        self.assertEqual(mock_session.get.call_count, 1)


if __name__ == '__main__':
    unittest.main()
