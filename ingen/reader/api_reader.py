#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.utils.app_http.http_util import execute_requests
from ingen.utils.json_df_convertors import get_json_to_df_convertor, DEFAULT_CONVERTOR


class APIReader:
    logger = logging.getLogger("APIReader")

    def __init__(self, requests, reader_params=None):
        self._requests = requests
        self._response_to_list = False
        self._reader_params = reader_params
        self.json_convertor = get_json_to_df_convertor()
        if reader_params:
            self._json_convertor_name = reader_params.get('json_convertor', DEFAULT_CONVERTOR)
            if reader_params.get('response_to_list'):
                self._json_convertor_name = 'response_to_list'
            self.json_convertor = get_json_to_df_convertor(self._json_convertor_name)

    def execute(self, data_node=None, data_key=None, meta=None):
        """
        Method that return the required dataframe from a list of urls(by appending the result from each url).
        param data_node: List of required nodes(of type list) from the api
        param data_key: List of keys (of type dictionary/string) from the api
        param meta: List of meta fields to be read from the response (see meta arg of pandas.json_normalize())
        """
        parsed_data = execute_requests(self._requests, self._reader_params)
        return self.json_convertor(parsed_data, data_node, data_key, meta)
