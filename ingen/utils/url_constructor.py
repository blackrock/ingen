#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from datetime import date
from urllib.parse import quote

from ingen.data_source.file_source import FileSource
from ingen.data_source.source_factory import SourceFactory


class UrlConstructor:
    """
    A utility class to construct URLs with given base URL and its URL params. URL params can be fetched from a file,
    a database or can be declared as a constant in the configuration file. More than one URL can be constructed to
    support batching.
    """
    URL_PARAM_SEPARATOR = "&"

    def __init__(self, url, url_query_params, batch=None, run_date=date.today(), source_factory=SourceFactory()):
        """
        Initialize with a base url and a list of url params. Optionally, at most one param can be used to create a
        batch of urls
        :param url: base url
        :param url_query_params: list of url params containing id and it's type
        :param batch: url_param id and batch_size
        :param run_date: run date passed via cmd line param
        """
        self.base_url = url
        self.url_query_params = url_query_params
        self.batch_config = batch
        self.run_date = run_date
        self.source_factory = source_factory

    def get_urls(self):
        """
        Constructs the URLs using the class variables and returns a list of URLs. If batching is off, list will contain
        only one URL.
        :return: list of URLs
        """
        batch_type = None
        if self.batch_config is not None:
            # batch_type defaults to query_param batch for backward compatibility
            batch_type = self.batch_config.get('batch_type', 'query_param')

        if self.url_query_params is None and batch_type is None:
            return [self.base_url]

        # path param is applied before query params
        if batch_type == 'path_param':
            urls = self.get_path_param_batch_urls(self.base_url, self.batch_config)
            return self.append_query_params(urls)
        elif batch_type == 'query_param':
            urls = [self.base_url]
            urls = self.append_query_params(urls)
            batch_id = self.batch_config.get('id')
            batch_size = self.batch_config.get('size', 2)
            return self.get_query_param_batch_urls(urls[0], batch_id, batch_size)
        else:
            urls = [self.base_url]
            return self.append_query_params(urls)

    def append_query_params(self, urls):
        if self.url_query_params is not None:
            urls = [url + self.get_params() for url in urls]
            return urls
        else:
            return urls

    def get_path_param_batch_urls(self, url, batch_config):
        source_config = batch_config.get('path_param_source')
        path_param_name = batch_config.get('path_param_name')
        data = None

        if source_config:
            data = self.get_data_from_source(source_config)

        urls = []
        if data is not None:
            for path_param in data[path_param_name]:
                urls.append(f"{url}/{path_param}")

        return urls

    def get_data_from_source(self, source_config, params=None):
        data_source = self.source_factory.parse_source(source_config, params)
        data = data_source.fetch()
        return data

    def get_query_param_batch_urls(self, url, batch_id, batch_size):
        """
        Replace the given url param in the url and create a list of urls
        :param url: url string with replaceable param id within curly braces
        :param batch_id: id of url param
        :param batch_size: batch size
        :return: list of urls with id replaced with actual values
        """
        values = self.fetch_param(self.get_param_by_id(batch_id))
        if values is None:
            raise ValueError(f"Could not fetch values for batch url param. id = {batch_id}")
        values = values.split(',')
        values_len = len(values)
        batches = [values[i: i + batch_size] for i in range(0, values_len, batch_size)]
        urls = []
        for batch in batches:
            urls.append(url.replace(f"{{{batch_id}}}", ",".join(batch)))
        return urls

    def get_param_by_id(self, id):
        if id is not None:
            return next(filter(lambda param: param.get('id') == id, self.url_query_params))

    def fetch_param(self, param):
        value = None
        if param.get('type') == "const":
            value = param.get('value')
            if value is not None:
                value = quote(param.get('value'))
        elif param.get('type') == "file":
            value = self.get_file_value(param)
        return value

    def get_params(self):
        """
        Construct the url param string
        :return: url param string, eg, `?key1=value1&key2=value2`
        """
        url_param = "?"
        for param in self.url_query_params:
            url_param += self.stringify_param(param) + "&"
        return url_param[:-1]  # removes extra ampersand at the end

    def stringify_param(self, param):
        key = param.get('id')
        if self.is_batch_query_param(key):  # batch param is fetched separately
            value = f"{{{key}}}"
        else:
            value = self.fetch_param(param)

        if value is None:
            value = ''

        return key + "=" + value

    def get_file_value(self, param):
        source = FileSource(param, {'run_date': self.run_date})
        data = source.fetch()
        return self.dest_column_of_data(data, param.get("dest_column"))

    def dest_column_of_data(self, data, dest_column):
        if data is not None and len(data) != 0:
            if dest_column is None:
                values = list(data.iloc[:, 0])  # converting first column of df to list
            else:
                values = data[dest_column].tolist()  # converting destination column of df to list
            values = [quote(str(value)) for value in values]
            return ','.join(values)

    def is_batch_query_param(self, key):
        if self.batch_config is not None:
            return self.batch_config.get('id') == key
