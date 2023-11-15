#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
from datetime import date

from ingen.data_source.source import DataSource
from ingen.reader.api_reader import APIReader
from ingen.utils.app_http.http_request import HTTPRequest
from ingen.utils.app_http.success_criterias import DEFAULT_STATUS_CRITERIA_OPTIONS, get_criteria_by_name
from ingen.utils.interpolators.Interpolator import Interpolator
from ingen.utils.timer import log_time
from ingen.utils.url_constructor import UrlConstructor

log = logging.getLogger()


class APISource(DataSource):
    """
    This class represents a API source
    """

    def __init__(self, source, params_map=None, interpolator=Interpolator()):
        """
        Loads a API source

        :param source : An interface source contains all the attributes i.e. api_id, url, data_col , data_key and more
        :param params_map : command line parameters
        """
        super().__init__(source.get('id'))
        if params_map is None:
            params_map = {}
        self._interpolator = interpolator
        self._url = source.get('url')
        self._url_params = source.get('url_params')
        self._batch = source.get('batch')
        self._data_node = source.get('data_node')
        self._data_key = source.get('data_key')
        self._meta = source.get('meta')
        self._auth = source.get('auth')
        self._response_to_list = source.get('response_to_list')
        self._run_date = params_map.get('run_date', date.today())
        # GET is set as default HTTP method for backward compatibility of config files
        self._method = source.get('method', 'GET')
        self._req_data = source.get('request_body')
        self._headers = self.parse_headers(source.get('headers'))
        self.reader_params = {
            'response_to_list': self._response_to_list,
            'retries': source.get('retries', 2),
            'interval': source.get('interval', 1),
            'interval_increment': source.get('interval_increment', 2),
            'success_criteria': get_criteria_by_name(source.get('success_criteria', 'status_criteria')),
            'criteria_options': source.get('criteria_options', DEFAULT_STATUS_CRITERIA_OPTIONS),
            'convertor_method': source.get('convertor_method'),
            'tasks_len': source.get('tasks_len', 1),
            'queue_size': source.get('queue_size', 1),
            'ssl': source.get('ssl', True),
            'ignore_failure': source.get('ignore_failure', True)
        }
        self._src_data_checks = source.get('src_data_checks', [])

    def fetch(self):
        """
        Calls the API from the url .

        :return: A DataFrame created using the result of the request made to the API
        """
        url_constructor = UrlConstructor(self._url, self._url_params, self._batch, self._run_date)
        urls = url_constructor.get_urls()
        requests = [HTTPRequest(url=url,
                                method=self._method,
                                headers=self._headers,
                                auth=self._auth,
                                data=self._req_data) for url in urls]
        url_reader = APIReader(requests, self.reader_params)
        return self.fetch_data(url_reader)

    @log_time
    def fetch_data(self, url_reader):
        """
        returns a DataFrame of data fetched from APISource.
        """
        return url_reader.execute(self._data_node, self._data_key, self._meta)

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src_data_checks

    def parse_headers(self, headers):
        """
        Interpolate header values
        :param headers: dict-like HTTP headers
        :return: dict of HTTP headers with interpolated values
        """
        return {key: self._interpolator.interpolate(value) for key, value in headers.items()} if headers else None
