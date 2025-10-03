#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.utils.app_http.aiohttp_retry import HTTPResponse
from ingen.utils.app_http.success_criterias import payload_criteria, status_criteria


class TestSuccessCriterias:
    def test_payload_criteria_success(self):
        status = 200
        headers = dict()
        response = {'done': True, 'data': {'random': 'data points'}}
        http_response = HTTPResponse(status, headers, response)

        options = {
            'key': 'done',
            'value': True
        }

        assert payload_criteria(http_response, options)

    def test_payload_criteria_failure(self):
        status = 200
        headers = dict()
        response = {'done': False, 'data': {'random': 'data points'}}
        http_response = HTTPResponse(status, headers, response)

        options = {
            'key': 'done',
            'value': True
        }

        assert not payload_criteria(http_response, options)

    def test_payload_criteria_with_error(self):
        status = 200
        headers = dict()
        response = {'done': True, 'data': {'some': 'thing'}, 'error': {'message': 'failure'}}

        http_response = HTTPResponse(status, headers, response)

        options = {
            'key': 'done',
            'value': True
        }

        assert not payload_criteria(http_response, options)

    def test_status_criteria_matches_given_status_code(self):
        http_response = HTTPResponse(201, dict(), None)
        options = {
            'status': 201
        }
        assert status_criteria(http_response, options)

    def test_status_criteria_fails_when_status_codes_are_diff(self):
        http_response = HTTPResponse(500, dict(), dict())
        options = {
            'status': 200
        }
        assert not status_criteria(http_response, options)

    def test_payload_criteria_success_data_list(self):
        status = 200
        headers = dict()
        response = [{'done': True, 'data': {'random': 'data points'}}]
        http_response = HTTPResponse(status, headers, response)
        options = {
            'key': 'done',
            'value': True
        }
        assert payload_criteria(http_response, options)

    def test_payload_criteria_success_data_list_failure(self):
        status = 200
        headers = dict()
        response = [{'done': True, 'data': {'random': 'data points'}}]
        http_response = HTTPResponse(status, headers, response)
        options = {
            'key': 'done',
            'value': False
        }
        assert not payload_criteria(http_response, options)
