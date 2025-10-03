#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import asyncio
import pytest

from ingen.utils.app_http.aiohttp_retry import http_retry_request


class SessionStub:
    """
    Helper class to create stub for Async Context Manager
    """
    
    def __init__(self):
        self.get_calls = []
        self.call_count = 0
        self.response = None

    async def __aenter__(self, *args, **kwargs):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass
    
    def get(self, *args, **kwargs):
        self.get_calls.append((args, kwargs))
        self.call_count += 1
        return ResponseContextStub(self.response)


class ResponseContextStub:
    def __init__(self, response):
        self.response = response
    
    async def __aenter__(self):
        return self.response
    
    async def __aexit__(self, *args):
        pass


class ResponseStub:
    def __init__(self, status=200, headers=None, data=None, should_raise=False):
        self.status = status
        self.headers = headers or {}
        self.data = data
        self.should_raise = should_raise
    
    async def json(self):
        if self.should_raise:
            raise Exception("Connection error")
        return self.data


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


class TestAiohttpRetry:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        yield
        self.loop.close()

    def test_http_get_retry(self):
        session_stub = SessionStub()
        response_stub = ResponseStub(
            status=200,
            headers={'Content-Type': 'application/json'},
            data={'data': 123}
        )
        session_stub.response = response_stub

        http_response = self.loop.run_until_complete(http_retry_request(session_stub,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=2,
                                                                        interval=1,
                                                                        success_criteria=passing_success_criteria))

        assert http_response.status == 200
        assert http_response.headers == {'Content-Type': 'application/json'}
        assert http_response.data == {'data': 123}
        assert session_stub.call_count == 1

    def test_http_retry_request_sends_none_when_success_criteria_fails(self):
        session_stub = SessionStub()
        response_stub = ResponseStub(
            headers={'Content-Type': 'application/json'},
            data={'done': False}
        )
        session_stub.response = response_stub

        http_response = self.loop.run_until_complete(http_retry_request(session_stub,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=2,
                                                                        interval=1,
                                                                        success_criteria=failing_success_criteria))

        assert http_response is None
        # one call + 2 retries
        assert session_stub.call_count == 3

    def test_http_retry_when_connection_exception_occurs(self):
        session_stub = SessionStub()
        response_stub = ResponseStub(should_raise=True)
        session_stub.response = response_stub

        with pytest.raises(ConnectionError):
            http_response = self.loop.run_until_complete(http_retry_request(session_stub,
                                                                            'get',
                                                                            'test.com',
                                                                            retries=2,
                                                                            interval=1))

        assert session_stub.call_count == 1

    def test_http_retry_when_retry_is_zero(self):
        session_stub = SessionStub()
        response_stub = ResponseStub(
            headers={'Content-Type': 'application/json'},
            data={'done': False}
        )
        session_stub.response = response_stub

        http_response = self.loop.run_until_complete(http_retry_request(session_stub,
                                                                        'get',
                                                                        'test.com',
                                                                        retries=0,
                                                                        success_criteria=failing_success_criteria))

        assert http_response is None
        # one call, no retries
        assert session_stub.call_count == 1
