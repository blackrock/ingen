#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import json
import logging

from ingen.reader.api_reader import APIReader
from ingen.utils.app_http.http_request import HTTPRequest
from ingen.utils.app_http.success_criterias import DEFAULT_STATUS_CRITERIA_OPTIONS, get_criteria_by_name
from ingen.utils.interpolators.Interpolator import Interpolator
from ingen.utils.path_parser import PathParser
from ingen.writer.dataframe_writer import DataFrameWriter

log = logging.getLogger()


def parse_headers(headers, params):
    """
    Interpolate header values
    params: dictionary for HTTP headers
    returns interpolated values of the dictionary
    """
    return {key: Interpolator(params).interpolate(value) for key, value in headers.items()} if headers else None


class ApiDestination:
    def __init__(self, params=None):
        self._params = params

    def handle(self, json_strings, destination_props):
        """
        Creates a list of HTTP Requests using json_strings and destination props
        Executes the HTTP requests using http_util
        Stores the response in raw_dataframe_store
        """
        api_request_props = destination_props.get('api_request_props')
        for json_string in json_strings:
            try:
                json.loads(json_string)
            except json.decoder.JSONDecodeError as err:
                log.error(f"Invalid JSON strings: {str(err)}")
                raise ValueError("Invalid JSON strings")

        path_parser = PathParser()
        requests = [HTTPRequest(url=path_parser.parse(api_request_props.get('url')),
                                method=api_request_props.get('method'),
                                headers=parse_headers(api_request_props.get('headers'), self._params),
                                auth=api_request_props.get('auth'),
                                data=json_string) for json_string in json_strings]

        api_response_props = destination_props.get('api_response_props')

        reader_props = {
            'retries': api_request_props.get('retries', 2),
            'interval': api_request_props.get('interval', 1),
            'success_criteria': get_criteria_by_name(api_request_props.get('success_criteria',
                                                                           get_criteria_by_name('status_criteria'))),
            'criteria_options': api_request_props.get('criteria_options', DEFAULT_STATUS_CRITERIA_OPTIONS),
            'tasks_len': api_request_props.get('tasks_len', 1),
            'queue_size': api_request_props.get('queue_size', 1),
            'ssl': api_request_props.get('ssl', True),
            'ignore_failure': api_request_props.get('ignore_failure', True)
        }

        reader = APIReader(requests, reader_props)
        response_data = reader.execute(api_response_props.get('data_node'),
                                       api_response_props.get('data_key'))

        if len(response_data) == 0:
            log.warning("Received empty response from API call. Writing empty dataframe to dataframe store.")

        writer = DataFrameWriter(response_data, {'id': api_response_props.get('dataframe_id')})
        writer.write()
