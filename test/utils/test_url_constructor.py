#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import unittest
from unittest.mock import patch, Mock

import pandas as pd

from ingen.utils.url_constructor import FileSource
from ingen.utils.url_constructor import UrlConstructor


class MyTestCase(unittest.TestCase):
    def test_url_constructor_with_no_params(self):
        url = "https://www.google.com"
        url_param = None

        expected_urls = ["https://www.google.com"]

        constructor = UrlConstructor(url, url_param)
        constructed_urls = constructor.get_urls()

        self.assertListEqual(expected_urls, constructed_urls)

    def test_url_with_const_param(self):
        url = "https://www.google.com"
        url_params = [
            {
                "id": "q",
                "type": "const",
                "value": "search-term"
            }
        ]

        expected_urls = ["https://www.google.com?q=search-term"]

        constructor = UrlConstructor(url, url_params)
        constructed_urls = constructor.get_urls()

        self.assertListEqual(expected_urls, constructed_urls)

    def test_url_with_file_source(self):
        url = "https://www.google.com"
        url_params = [
            {
                "id": "q",
                "type": "file",
                "file_path": "../path/to/test/file.csv",
                "delimiter": ",",
                "columns": ["column_name"],
                "dest_column": "column_name"
            }
        ]

        file_source_result = pd.DataFrame(['Y', 'N'], columns=["column_name"])
        expected_urls = ["https://www.google.com?q=Y,N"]

        with patch.object(FileSource, 'fetch', return_value=file_source_result):
            constructor = UrlConstructor(url, url_params)
            constructed_urls = constructor.get_urls()
            self.assertListEqual(expected_urls, constructed_urls)

    def test_batch_urls(self):
        url = "https://google.com"
        batch = {
            'size': 2,
            'id': 'accountIds'
        }
        url_params = [
            {
                "id": "accountIds",
                "type": "file",
                "file_path": "../path/to/test/file.csv",
                "delimiter": ",",
                "columns": ["column_name"],
                "dest_column": "column_name"
            }
        ]

        file_source_result = pd.DataFrame(['A1', 'A2', 'A3', 'A4'], columns=["column_name"])
        expected_urls = ["https://google.com?accountIds=A1,A2", "https://google.com?accountIds=A3,A4"]

        with patch.object(FileSource, 'fetch', return_value=file_source_result):
            constructor = UrlConstructor(url, url_params, batch)
            constructed_urls = constructor.get_urls()
            self.assertListEqual(expected_urls, constructed_urls)

    def test_url_params_are_safe(self):
        url = "https://google.com"
        url_params = [{
            "id": "query",
            "type": "const",
            "value": "value with spaces & special chars."
        }
        ]

        expected_urls = ["https://google.com?query=value%20with%20spaces%20%26%20special%20chars"]

        constructor = UrlConstructor(url, url_params)
        constructed_urls = constructor.get_urls()
        self.assertListEqual(expected_urls, constructed_urls)

    def test_empty_url_param(self):
        url = "https://google.com"
        url_params = [{
            "id": "query",
            "type": "const"
        }, {
            "id": "loc"
        }, {
            "id": "add",
            "type": "db",
            "db_token": "DSREAD",
            "query": "select cde from fake_db where tbl_desc = 'fake_table'"
        }]

        db_source_result = pd.DataFrame()
        expected_urls = ["https://google.com?query=&loc=&add="]
        with patch.object(DBSource, 'fetch', return_value=db_source_result):
            constructor = UrlConstructor(url, url_params)
            constructed_urls = constructor.get_urls()
            self.assertListEqual(expected_urls, constructed_urls)

    def test_url_with_none_dest_column(self):
        url = "https://www.google.com"
        url_params = [
            {
                "id": "q",
                "type": "file",
                "file_path": "../path/to/test/file.csv",
                "delimiter": ",",
                "columns": ["column_name"],
            }
        ]

        file_source_result = pd.DataFrame(['Y', 'N'])
        expected_urls = ["https://www.google.com?q=Y,N"]

        with patch.object(FileSource, 'fetch', return_value=file_source_result):
            constructor = UrlConstructor(url, url_params)
            constructed_urls = constructor.get_urls()
            self.assertListEqual(expected_urls, constructed_urls)

    def test_batch_with_path_params(self):
        url = "https://www.host.com"

        batch = {
            'batch_type': 'path_param',
            'path_param_name': 'ids',
            'path_param_source': {
                'id': 'dataframe_name',
                'type': 'datastore'
            }
        }

        source_df = pd.DataFrame({
            'ids': [1, 2, 3, 4]
        })
        mock_data_source_factory = Mock()
        mock_data_source = Mock()
        mock_data_source_factory.parse_source.return_value = mock_data_source
        mock_data_source.fetch.return_value = source_df

        expected_urls = [
            'https://www.host.com/1',
            'https://www.host.com/2',
            'https://www.host.com/3',
            'https://www.host.com/4',
        ]

        constructor = UrlConstructor(url, None, batch, source_factory=mock_data_source_factory)
        constructed_urls = constructor.get_urls()
        self.assertListEqual(constructed_urls, expected_urls)


if __name__ == '__main__':
    unittest.main()
