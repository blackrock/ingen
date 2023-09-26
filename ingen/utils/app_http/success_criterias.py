"""
HTTP Success Criteria

This module contains the functions that can be used to define success of a
HTTP response. Every function takes two inputs -
1. HTTPResponse - a namedtuple with following fields
    status:     HTTP status code
    headers:    HTTP response headers
    data:       HTTP response data

2. options - a dict containing criteria specific fields

The function should return True if the defined criteria is met by the given
HTTP response, otherwise False.
"""
#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

DEFAULT_STATUS_CRITERIA_OPTIONS = {'status': 200}

logger = logging.getLogger()


def payload_criteria(response, options):
    """
    Checks if a given field is present in the response and is equal to the provided value
    and there's no 'error' field in the response
    :param response: HTTPResponse namedtuple
    :param options: an options dict containing following keys:
                options[key]   = Field name in the response
                options[value] = Expected value of 'data[key]'
    :return: True if 'key' is present in data and 'data[key] == value', otherwise False
    """
    key = options.get('key')
    value = options.get('value')

    if key is None or value is None:
        raise KeyError("missing key/value payload_success options")

    if isinstance(response.data, list):
        if (key in response.data[0] and response.data[0][key] != value):
            # in case of success criteria is not met, log error
            logger.error(f"An exception occured while processing this request : {response.data} ")
        return 'error' not in response.data[0] and key in response.data[0] and response.data[0][key] == value

    return 'error' not in response.data and key in response.data and response.data[key] == value


def status_criteria(response, options):
    """
    Checks if the response status code is equal to the expected code passed in options
    :param response: HTTPResponse namedtuple
    :param options: options[status_code] = HTTP status code
    :return: True or False
    """
    expected_status = options.get('status')

    if expected_status is None:
        raise KeyError("missing status_code for status_criteria")

    return expected_status == response.status


CRITERIA_FUNCTIONS = {
    'payload_criteria': payload_criteria,
    'status_criteria': status_criteria
}


def get_criteria_by_name(criteria_name):
    return CRITERIA_FUNCTIONS.get(criteria_name)
