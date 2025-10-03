#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import pytest

from aiohttp import BasicAuth

from ingen.utils.app_http.http_request import HTTPRequest
from ingen.utils.app_http.aiohttp_retry import HTTPResponse
from ingen.utils.app_http.http_util import api_auth, execute_requests
from ingen.utils.app_http.success_criterias import get_criteria_by_name, DEFAULT_STATUS_CRITERIA_OPTIONS


class TestHttpUtil:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.auth = {'username': 'user', 'pwd': 'pwd', 'type': 'BasicAuth'}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.request_params = {
            'retries': 2,
            'interval': 1,
            'interval_increment': 2,
            'success_criteria': get_criteria_by_name('status_criteria'),
            'criteria_options': DEFAULT_STATUS_CRITERIA_OPTIONS
        }
        yield
        self.loop.close()

    def test_basic_auth(self, monkeypatch):
        auth_config = {
            'type': 'BasicAuth',
            'username': 'username',
            'pwd': 'password'
        }
        
        class PropertiesStub:
            @staticmethod
            def get_property(key):
                return 'username'
        
        monkeypatch.setattr('ingen.utils.app_http.http_util.Properties', PropertiesStub)
        auth = api_auth(auth_config)
        assert isinstance(auth, BasicAuth)

    def test_single_request(self, monkeypatch):
        requests = [HTTPRequest(url="www.test-url.com", method="GET")]
        response_body = {
            'name': 'Amit',
            'age': 32
        }
        empty_headers = dict()
        http_response = HTTPResponse(200, empty_headers, response_body)
        expected_response = [response_body]

        # The stub should return a coroutine that resolves to the HTTPResponse
        async def stub_http_retry_request(*args, **kwargs):
            return http_response
        
        monkeypatch.setattr('ingen.utils.app_http.http_util.http_retry_request', stub_http_retry_request)

        parsed_data = execute_requests(requests, self.request_params)
        assert parsed_data == expected_response

    def test_multiple_requests(self, monkeypatch):
        requests = [
            HTTPRequest(url="www.test-url.com", method="GET"),
            HTTPRequest(url="www.test-url2.com", method="GET")
        ]
        response_json_1 = {
            'name': 'Amit',
            'age': '31'
        }
        response_json_2 = {
            'name': 'Kali',
            'age': '30'
        }
        http_response_1 = HTTPResponse(200, dict(), response_json_1)
        http_response_2 = HTTPResponse(200, dict(), response_json_2)

        expected_responses = [response_json_1, response_json_2]

        # The stub should return coroutines that resolve to HTTPResponse objects
        responses = [http_response_1, http_response_2]
        response_index = 0
        
        async def stub_http_retry_request(*args, **kwargs):
            nonlocal response_index
            result = responses[response_index]
            response_index += 1
            return result

        monkeypatch.setattr('ingen.utils.app_http.http_util.http_retry_request', stub_http_retry_request)

        parsed_data = execute_requests(requests, self.request_params)
        assert parsed_data == expected_responses
